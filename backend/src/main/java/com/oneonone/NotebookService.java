package com.oneonone;

import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.ByteBuffersDirectory;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.encryption.InvalidPasswordException;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

/**
 * The document notebook. A learner's text PDFs are kept as page-numbered text (the file itself is not
 * stored). Search builds a small Lucene index, scored with BM25, from only that learner's selected
 * sources on each query, so no other learner's pages can ever be returned. Answers quote passages by
 * file and page; when nothing relevant is found the notebook says so instead of asking the model.
 */
@Service
public class NotebookService {

  static final int MAX_BYTES = 10 * 1024 * 1024, MAX_PAGES = 100, MAX_SOURCES = 20, PASSAGE_WORDS = 120, STEP_WORDS = 90;
  private static final Pattern DEFINITION = Pattern.compile(
    "(?:^|(?<=[.!?]\\s))([A-Z][A-Za-z0-9 ()'-]{2,60}?) (is|are|means|refers to|describes) ([^.!?]{12,280}[.!?])"
  );

  private static final Set<String> NOT_A_TERM = Set.of(
    "each", "every", "this", "that", "these", "those", "it", "they", "some", "all", "any", "there", "here", "such", "one"
  );

  public record Passage(String sourceId, String title, int page, String text, float score) {}

  final Store store;
  final TutorService tutor;

  public NotebookService(Store store, TutorService tutor) {
    this.store = store;
    this.tutor = tutor;
  }

  // ---- sources ----

  @Transactional
  public Map<String, Object> ingest(String user, String fileName, byte[] bytes) {
    if (bytes == null || bytes.length == 0) throw new IllegalArgumentException("Choose a PDF to add.");
    if (bytes.length > MAX_BYTES) throw new IllegalArgumentException("PDFs can be up to 10 MB. Split or compress this one.");
    if (bytes.length < 5 || !new String(bytes, 0, 5, java.nio.charset.StandardCharsets.US_ASCII).equals("%PDF-")) throw new IllegalArgumentException(
      "That isn't a PDF. Slides and documents can be exported to PDF first."
    );
    Integer owned = store.db.queryForObject("select count(*) from notebook_sources where member_id=?", Integer.class, user);
    if (owned != null && owned >= MAX_SOURCES) throw new IllegalArgumentException("You can keep up to 20 sources. Remove one to add another.");
    List<String> pages = new ArrayList<>();
    try (var pdf = Loader.loadPDF(bytes)) {
      if (pdf.isEncrypted() && !pdf.getCurrentAccessPermission().canExtractContent()) throw new IllegalArgumentException(
        "This PDF doesn't allow its text to be copied. Export an unrestricted copy."
      );
      int n = pdf.getNumberOfPages();
      if (n == 0) throw new IllegalArgumentException("This PDF has no pages.");
      if (n > MAX_PAGES) throw new IllegalArgumentException("PDFs can have up to 100 pages; this one has " + n + ". Split it into parts.");
      var stripper = new PDFTextStripper();
      for (int p = 1; p <= n; p++) {
        stripper.setStartPage(p);
        stripper.setEndPage(p);
        pages.add(stripper.getText(pdf).replaceAll("[\\s\\u00A0]+", " ").strip());
      }
    } catch (InvalidPasswordException e) {
      throw new IllegalArgumentException("This PDF is password-protected. Export a copy without a password.");
    } catch (IOException e) {
      throw new IllegalArgumentException("This PDF couldn't be read. It may be damaged; try exporting it again.");
    }
    int chars = pages.stream().mapToInt(String::length).sum();
    if (chars < 40 * pages.size()) throw new IllegalArgumentException(
      "This PDF has almost no text layer: it looks like scanned images. Use a text PDF, or run it through OCR first."
    );
    String id = "src-" + UUID.randomUUID();
    String name = fileName == null || fileName.isBlank() ? "document.pdf" : fileName.replaceAll("[\\\\/]", "_");
    if (name.length() > 255) name = name.substring(0, 255);
    String title = name.replaceAll("(?i)\\.pdf$", "");
    if (title.length() > 200) title = title.substring(0, 200);
    store.db.update(
      "insert into notebook_sources(id,member_id,title,file_name,pages,bytes) values(?,?,?,?,?,?)",
      id, user, title, name, pages.size(), bytes.length
    );
    for (int p = 0; p < pages.size(); p++) store.db.update("insert into notebook_pages(source_id,page,text) values(?,?,?)", id, p + 1, pages.get(p));
    return source(user, id);
  }

  public List<Map<String, Object>> sources(String user) {
    return store.db.queryForList(
      "select id,title,file_name as fileName,pages,bytes,created_at as createdAt from notebook_sources where member_id=? order by created_at desc",
      user
    ).stream().map(NotebookService::camel).toList();
  }

  Map<String, Object> source(String user, String id) {
    var rows = store.db.queryForList(
      "select id,title,file_name as fileName,pages,bytes,created_at as createdAt from notebook_sources where member_id=? and id=?",
      user, id
    );
    if (rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "This source could not be found.");
    return camel(rows.getFirst());
  }

  /** Removes the source and its pages. Cards made from it stay (they are the learner's own edits) but lose the link. */
  @Transactional
  public void delete(String user, String id) {
    source(user, id);
    store.db.update("update notebook_cards set source_id=null, page=null, updated_at=CURRENT_TIMESTAMP where member_id=? and source_id=?", user, id);
    store.db.update("delete from notebook_pages where source_id=?", id);
    store.db.update("delete from notebook_sources where member_id=? and id=?", user, id);
  }

  // ---- search and answers ----

  /** BM25 over the learner's selected sources (all of them when none are selected), best passages first. */
  public List<Passage> search(String user, String query, List<String> sourceIds, int limit) {
    if (query == null || query.isBlank() || query.length() > 500) throw new IllegalArgumentException("Search with up to 500 characters.");
    var rows = pages(user, sourceIds);
    if (rows.isEmpty()) return List.of();
    try (Analyzer analyzer = new EnglishAnalyzer(); var dir = new ByteBuffersDirectory()) {
      try (var writer = new IndexWriter(dir, new IndexWriterConfig(analyzer).setSimilarity(new BM25Similarity()))) {
        for (var row : rows) for (String passage : passages(row.get("text").toString())) {
          var doc = new Document();
          doc.add(new TextField("text", passage, Field.Store.YES));
          doc.add(new StoredField("source", row.get("source_id").toString()));
          doc.add(new StoredField("title", row.get("title").toString()));
          doc.add(new StoredField("page", ((Number) row.get("page")).intValue()));
          writer.addDocument(doc);
        }
      }
      // terms built from the analyzer directly: no query syntax, so any text is safe to search
      var q = new BooleanQuery.Builder();
      int terms = 0;
      try (TokenStream ts = analyzer.tokenStream("text", query)) {
        var attr = ts.addAttribute(CharTermAttribute.class);
        ts.reset();
        while (ts.incrementToken() && terms < 64) {
          q.add(new TermQuery(new Term("text", attr.toString())), BooleanClause.Occur.SHOULD);
          terms++;
        }
        ts.end();
      }
      if (terms == 0) throw new IllegalArgumentException("Search with a few meaningful words.");
      try (var reader = DirectoryReader.open(dir)) {
        var searcher = new IndexSearcher(reader);
        searcher.setSimilarity(new BM25Similarity());
        var out = new ArrayList<Passage>();
        for (ScoreDoc hit : searcher.search(q.build(), Math.max(1, Math.min(limit, 10))).scoreDocs) {
          var d = searcher.storedFields().document(hit.doc);
          out.add(new Passage(d.get("source"), d.get("title"), d.getField("page").numericValue().intValue(), d.get("text"), hit.score));
        }
        return out;
      }
    } catch (IOException e) {
      throw new IllegalStateException(e);
    }
  }

  /**
   * An answer from the selected sources only. With no relevant passage the notebook says so and the model is
   * not asked; without a model the passages themselves are the answer. Citations are checked against the
   * passages actually supplied.
   */
  public Map<String, Object> ask(String user, String question, List<String> sourceIds) {
    if (question == null || question.isBlank() || question.length() > 1000) throw new IllegalArgumentException("Ask a question of up to 1000 characters.");
    var hits = search(user, question, sourceIds, 5);
    var out = new LinkedHashMap<String, Object>();
    out.put("passages", hits.stream().map(NotebookService::view).toList());
    if (hits.isEmpty()) {
      out.put("answered", false);
      out.put("text", "Your selected sources don't mention this. Add a source that covers it, or ask the tutor in a notebook.");
      out.put("citations", List.of());
      out.put("method", "search");
      return out;
    }
    if (!tutor.aiConfigured()) {
      out.put("answered", null);
      out.put("text", "These are the closest passages in your sources. Add a Gemini key to get a written answer that cites them.");
      out.put("citations", List.of());
      out.put("method", "search");
      return out;
    }
    var input = new StringBuilder("Passages:\n");
    for (int i = 0; i < hits.size(); i++) input.append("[").append(i + 1).append("] (").append(hits.get(i).title()).append(", page ")
      .append(hits.get(i).page()).append(") ").append(hits.get(i).text()).append("\n");
    input.append("\nQuestion: ").append(question);
    var answer = tutor.generateJson(
      user,
      "You answer a student's question using only the numbered passages from their own documents. Cite every claim with its passage number in square brackets, like [2]. If the passages do not answer the question, say so plainly, set answered to false and do not use outside knowledge. Be concise.",
      input.toString(),
      Map.of(
        "text", Map.of("type", "string"),
        "answered", Map.of("type", "boolean"),
        "citations", Map.of("type", "array", "items", Map.of("type", "integer"))
      )
    );
    List<Map<String, Object>> cited = new ArrayList<>();
    for (Object c : answer.get("citations") instanceof List<?> l ? l : List.of()) {
      int n = c instanceof Number num ? num.intValue() : -1;
      if (n >= 1 && n <= hits.size() && cited.stream().noneMatch(x -> x.get("n").equals(n))) {
        var v = new LinkedHashMap<>(view(hits.get(n - 1)));
        v.put("n", n);
        cited.add(v);
      }
    }
    out.put("answered", Boolean.TRUE.equals(answer.get("answered")) && !cited.isEmpty());
    out.put("text", Store.text(answer, "text", ""));
    out.put("citations", cited);
    out.put("method", "model");
    return out;
  }

  // ---- revision cards ----

  /** Drafts cards from one page (or the whole source): by the model when configured, else from the text's own definitions. */
  @Transactional
  public List<Map<String, Object>> draftCards(String user, String sourceId, Integer page) {
    var src = source(user, sourceId);
    var rows = store.db.queryForList(
      "select page,text from notebook_pages where source_id=?" + (page == null ? "" : " and page=?") + " order by page",
      page == null ? new Object[] { sourceId } : new Object[] { sourceId, page }
    );
    if (rows.isEmpty()) throw new IllegalArgumentException("Choose a page in this source.");
    List<String[]> drafts = new ArrayList<>(); // {front, back, page}
    String method;
    if (tutor.aiConfigured()) {
      var text = new StringBuilder();
      for (var r : rows) if (text.length() < 12000) text.append("(page ").append(r.get("page")).append(") ").append(r.get("text")).append("\n");
      var made = tutor.generateJson(
        user,
        "Write up to 6 revision flashcards from this study material: a short question on the front and a short, exact answer on the back, using only facts the material states. Give each card the page it came from.",
        text.toString(),
        Map.of("cards", Map.of("type", "array", "items", Map.of(
          "type", "object",
          "properties", Map.of("front", Map.of("type", "string"), "back", Map.of("type", "string"), "page", Map.of("type", "integer")),
          "required", List.of("front", "back", "page")
        )))
      );
      for (var c : Store.items(made.get("cards"))) drafts.add(new String[] { Store.text(c, "front", ""), Store.text(c, "back", ""), Store.text(c, "page", "") });
      method = "model";
    } else {
      for (var r : rows) for (String[] d : definitions(r.get("text").toString())) drafts.add(new String[] { d[0], d[1], r.get("page").toString() });
      method = "text";
    }
    Set<Integer> valid = new HashSet<>();
    for (var r : rows) valid.add(((Number) r.get("page")).intValue());
    List<Map<String, Object>> out = new ArrayList<>();
    for (String[] d : drafts) {
      if (out.size() >= 6 || d[0].isBlank() || d[1].isBlank()) continue;
      Integer p;
      try {
        p = Integer.valueOf(d[2]);
      } catch (NumberFormatException e) {
        p = null;
      }
      if (p == null || !valid.contains(p)) p = page != null ? page : ((Number) rows.getFirst().get("page")).intValue();
      String id = "card-" + UUID.randomUUID();
      store.db.update(
        "insert into notebook_cards(id,member_id,source_id,page,front,back,drafted_by) values(?,?,?,?,?,?,?)",
        id, user, src.get("id"), p, clip(d[0], 500), clip(d[1], 2000), method
      );
      out.add(card(user, id));
    }
    return out;
  }

  /** "X is Y." style sentences become "What is X?" / the sentence. Honest and limited: it only reuses the text. */
  static List<String[]> definitions(String text) {
    List<String[]> out = new ArrayList<>();
    Matcher m = DEFINITION.matcher(text);
    while (m.find() && out.size() < 6) {
      String term = m.group(1).strip();
      String first = term.split(" ")[0], predicate = m.group(3).strip().split("[ ,]")[0];
      // "Each vertex is marked…" is a statement, not a definition: skip determiner subjects and passive verbs
      if (term.split(" ").length > 6 || NOT_A_TERM.contains(first.toLowerCase(Locale.ROOT)) || predicate.endsWith("ed")) continue;
      if (List.of("A", "An", "The").contains(first)) term = first.toLowerCase(Locale.ROOT) + term.substring(first.length());
      out.add(new String[] { (m.group(2).equals("are") ? "What are " : "What is ") + term + "?", m.group(0).strip() });
    }
    return out;
  }

  public List<Map<String, Object>> cards(String user) {
    return store.db.queryForList(
      "select c.id,c.source_id as sourceId,s.title as sourceTitle,c.page,c.front,c.back,c.drafted_by as draftedBy,c.recall,c.recalled_at as recalledAt,c.updated_at as updatedAt " +
      "from notebook_cards c left join notebook_sources s on s.id=c.source_id where c.member_id=? order by c.created_at desc",
      user
    ).stream().map(NotebookService::camel).toList();
  }

  Map<String, Object> card(String user, String id) {
    return cards(user).stream().filter(c -> id.equals(c.get("id"))).findFirst()
      .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "This card could not be found."));
  }

  public Map<String, Object> editCard(String user, String id, String front, String back) {
    if (front == null || front.isBlank() || front.length() > 500 || back == null || back.isBlank() || back.length() > 2000) throw new IllegalArgumentException(
      "A card needs a front of up to 500 and a back of up to 2000 characters."
    );
    card(user, id);
    store.db.update("update notebook_cards set front=?, back=?, updated_at=CURRENT_TIMESTAMP where member_id=? and id=?", front.strip(), back.strip(), user, id);
    return card(user, id);
  }

  /** Self-reported recall: kept on the card only, never counted as graded evidence or mastery. */
  public Map<String, Object> recall(String user, String id, String rating) {
    if (!List.of("again", "hard", "good", "easy").contains(rating)) throw new IllegalArgumentException("Rate your recall as again, hard, good or easy.");
    card(user, id);
    store.db.update("update notebook_cards set recall=?, recalled_at=CURRENT_TIMESTAMP where member_id=? and id=?", rating, user, id);
    return card(user, id);
  }

  public void deleteCard(String user, String id) {
    card(user, id);
    store.db.update("delete from notebook_cards where member_id=? and id=?", user, id);
  }

  // ---- helpers ----

  /** Page text for the learner's own sources, restricted to the selection; ids that aren't theirs match nothing. */
  private List<Map<String, Object>> pages(String user, List<String> sourceIds) {
    var ids = sourceIds == null ? List.<String>of() : sourceIds.stream().distinct().limit(MAX_SOURCES).toList();
    String filter = ids.isEmpty() ? "" : " and s.id in (" + String.join(",", Collections.nCopies(ids.size(), "?")) + ")";
    List<Object> args = new ArrayList<>(List.of(user));
    args.addAll(ids);
    return store.db.queryForList(
      "select p.source_id,s.title,p.page,p.text from notebook_pages p join notebook_sources s on s.id=p.source_id where s.member_id=?" + filter,
      args.toArray()
    );
  }

  /** Overlapping windows of words, so a passage that spans a sentence break is still found whole. */
  static List<String> passages(String text) {
    String[] words = text.split(" ");
    if (words.length <= PASSAGE_WORDS) return text.isBlank() ? List.of() : List.of(text);
    List<String> out = new ArrayList<>();
    for (int i = 0; i < words.length; i += STEP_WORDS) {
      out.add(String.join(" ", Arrays.copyOfRange(words, i, Math.min(words.length, i + PASSAGE_WORDS))));
      if (i + PASSAGE_WORDS >= words.length) break;
    }
    return out;
  }

  static Map<String, Object> view(Passage p) {
    var v = new LinkedHashMap<String, Object>();
    v.put("sourceId", p.sourceId());
    v.put("title", p.title());
    v.put("page", p.page());
    v.put("text", p.text());
    v.put("score", Math.round(p.score() * 100) / 100.0);
    return v;
  }

  /** H2 and PostgreSQL may lower-case column aliases; the API always uses camelCase. */
  private static Map<String, Object> camel(Map<String, Object> row) {
    var out = new LinkedHashMap<String, Object>();
    for (var e : row.entrySet()) {
      String k = e.getKey();
      for (String name : List.of("fileName", "createdAt", "sourceId", "sourceTitle", "draftedBy", "recalledAt", "updatedAt")) if (k.equalsIgnoreCase(name)) k = name;
      Object v = e.getValue() instanceof java.sql.Timestamp t ? t.toInstant().toString() : e.getValue();
      out.put(k, v);
    }
    return out;
  }

  private static String clip(String s, int n) {
    return s.length() <= n ? s : s.substring(0, n);
  }
}
