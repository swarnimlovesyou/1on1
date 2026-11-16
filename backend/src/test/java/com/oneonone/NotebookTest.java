package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.encryption.AccessPermission;
import org.apache.pdfbox.pdmodel.encryption.StandardProtectionPolicy;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

class NotebookTest {

  Store store;
  NotebookService notebook;

  static final String GRAPHS =
    "Breadth-first search explores a graph level by level using a queue. A queue is a first-in first-out structure. " +
    "Each vertex is marked when it is discovered so that it is never added twice.";
  static final String HEAPS =
    "A binary heap is a complete binary tree stored in an array. The smallest key sits at the root of a min-heap. " +
    "Services were deployed behind a priority queue so urgent jobs ran first.";

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(
      new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", "")
    );
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql", "V4__document_notebook.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    var progress = new ProgressService(store);
    var tutor = new TutorService(store, new TraceEngine(), new ExecutionService(store, progress));
    tutor.key = ""; // no model: search-only answers and cards drafted from the text
    tutor.model = "gemini-3.1-flash-lite";
    notebook = new NotebookService(store, tutor);
  }

  /** A real PDF with one page per text (blank text gives an image-like page with no text layer). */
  static byte[] pdf(String... pages) throws Exception {
    return lockedPdf(null, pages);
  }

  static byte[] lockedPdf(String password, String... pages) throws Exception {
    try (var doc = new PDDocument(); var out = new ByteArrayOutputStream()) {
      var font = new PDType1Font(Standard14Fonts.FontName.HELVETICA);
      for (String text : pages) {
        var page = new PDPage();
        doc.addPage(page);
        try (var cs = new PDPageContentStream(doc, page)) {
          if (!text.isEmpty()) {
            cs.beginText();
            cs.setFont(font, 10);
            cs.setLeading(13);
            cs.newLineAtOffset(40, 740);
            for (String line : text.split("(?<=\\G.{90})")) {
              cs.showText(line);
              cs.newLine();
            }
            cs.endText();
          }
        }
      }
      if (password != null) {
        var policy = new StandardProtectionPolicy("owner-" + password, password, new AccessPermission());
        policy.setEncryptionKeyLength(128);
        doc.protect(policy);
      }
      doc.save(out);
      return out.toByteArray();
    }
  }

  @Test
  void textPdfsKeepTheirPagesAndBadFilesAreExplained() throws Exception {
    var src = notebook.ingest("alice", "algorithms notes.pdf", pdf(GRAPHS, HEAPS));
    assertEquals("algorithms notes", src.get("title"));
    assertEquals(2, ((Number) src.get("pages")).intValue());
    assertTrue(store.db.queryForObject("select text from notebook_pages where source_id=? and page=2", String.class, src.get("id")).contains("binary heap"));

    var notPdf = assertThrows(IllegalArgumentException.class, () -> notebook.ingest("alice", "slides.pptx", "PK\u0003\u0004 not a pdf".getBytes()));
    assertTrue(notPdf.getMessage().contains("isn't a PDF"));
    var big = new byte[NotebookService.MAX_BYTES + 1];
    System.arraycopy("%PDF-".getBytes(), 0, big, 0, 5);
    assertTrue(assertThrows(IllegalArgumentException.class, () -> notebook.ingest("alice", "big.pdf", big)).getMessage().contains("10 MB"));
    String[] many = new String[101];
    Arrays.fill(many, GRAPHS);
    assertTrue(assertThrows(IllegalArgumentException.class, () -> notebook.ingest("alice", "long.pdf", pdf(many))).getMessage().contains("101"));
    assertTrue(assertThrows(IllegalArgumentException.class, () -> notebook.ingest("alice", "scan.pdf", pdf("", "", ""))).getMessage().contains("scanned"));
    assertTrue(assertThrows(IllegalArgumentException.class, () -> notebook.ingest("alice", "locked.pdf", lockedPdf("secret", GRAPHS))).getMessage().contains("password"));
    assertEquals(1, notebook.sources("alice").size(), "nothing half-saved from a refused file");
  }

  @Test
  void searchCitesTheFileAndPageAndUnderstandsWordForms() throws Exception {
    var src = notebook.ingest("alice", "notes.pdf", pdf(GRAPHS, HEAPS));
    var hits = notebook.search("alice", "how does a min-heap keep the smallest key?", List.of(), 5);
    assertEquals(2, hits.getFirst().page());
    assertEquals("notes", hits.getFirst().title());
    assertEquals(src.get("id"), hits.getFirst().sourceId());
    assertEquals(2, notebook.search("alice", "deploying services", List.of(), 5).getFirst().page(), "stemming: deploying finds deployed");
    assertTrue(notebook.search("alice", "photosynthesis chlorophyll", List.of(), 5).isEmpty());
    assertThrows(IllegalArgumentException.class, () -> notebook.search("alice", "the and of", List.of(), 5), "only stop words");
    assertEquals(1, notebook.search("alice", "queue", List.of(src.get("id").toString()), 5).stream().map(NotebookService.Passage::page).filter(p -> p == 1).count());
  }

  @Test
  void oneLearnerNeverReachesAnothersSources() throws Exception {
    var hers = notebook.ingest("alice", "private.pdf", pdf(GRAPHS));
    String id = hers.get("id").toString();
    assertTrue(notebook.search("bob", "queue vertex", List.of(id), 5).isEmpty(), "naming her source id finds nothing");
    assertTrue(notebook.search("bob", "queue vertex", List.of(), 5).isEmpty());
    assertTrue(notebook.sources("bob").isEmpty());
    assertThrows(ResponseStatusException.class, () -> notebook.delete("bob", id));
    assertThrows(ResponseStatusException.class, () -> notebook.draftCards("bob", id, null));
    assertEquals(1, notebook.sources("alice").size());
  }

  @Test
  void answersSayWhenTheSourcesAreSilentAndOtherwiseShowPassages() throws Exception {
    notebook.ingest("alice", "notes.pdf", pdf(GRAPHS, HEAPS));
    var none = notebook.ask("alice", "what is photosynthesis", List.of());
    assertEquals(false, none.get("answered"));
    assertTrue(none.get("text").toString().contains("don't mention"));
    var some = notebook.ask("alice", "what does breadth-first search use", List.of());
    assertNull(some.get("answered"), "without a model it neither claims nor denies an answer");
    assertEquals(1, ((Map<?, ?>) ((List<?>) some.get("passages")).getFirst()).get("page"));
  }

  @Test
  void cardsAreDraftedFromTheTextEditedAndRecallStaysSelfReported() throws Exception {
    var src = notebook.ingest("alice", "notes.pdf", pdf(GRAPHS, HEAPS));
    String id = src.get("id").toString();
    var drafted = notebook.draftCards("alice", id, 1);
    assertFalse(drafted.isEmpty());
    var card = drafted.getFirst();
    assertEquals("What is a queue?", card.get("front"), card.toString());
    assertEquals(1, ((Number) card.get("page")).intValue());
    assertEquals("text", card.get("draftedBy"));

    var edited = notebook.editCard("alice", card.get("id").toString(), "What does BFS use?", "A queue, so vertices come out level by level.");
    assertEquals("What does BFS use?", edited.get("front"));
    assertThrows(ResponseStatusException.class, () -> notebook.editCard("bob", card.get("id").toString(), "x", "y"));
    assertEquals("good", notebook.recall("alice", card.get("id").toString(), "good").get("recall"));
    assertThrows(IllegalArgumentException.class, () -> notebook.recall("alice", card.get("id").toString(), "mastered"));
    assertEquals(0, store.db.queryForObject("select count(*) from learning_events", Integer.class), "recall is never graded evidence");

    notebook.delete("alice", id);
    var kept = notebook.cards("alice").stream().filter(c -> c.get("id").equals(card.get("id"))).findFirst().orElseThrow();
    assertNull(kept.get("sourceId"), "cards outlive their source, unlinked");
    assertEquals(0, store.db.queryForObject("select count(*) from notebook_pages where source_id=?", Integer.class, id));
  }

  @Test
  void definitionsAndPassagesAreSplitSensibly() {
    assertEquals(2, NotebookService.definitions("A queue is a first-in first-out structure. Stacks are last-in first-out structures.").size());
    assertTrue(NotebookService.definitions("no definitions here at all").isEmpty());
    var d = NotebookService.definitions("A queue is a first-in first-out structure. Each vertex is marked when it is first seen. It is a very useful idea.");
    assertEquals(1, d.size(), "statements about 'each vertex' or 'it' are not definitions");
    assertEquals("What is a queue?", d.getFirst()[0]);
    assertTrue(NotebookService.definitions("The root is reached first by every search path.").isEmpty(), "passive verb");
    String words = String.join(" ", Collections.nCopies(300, "w"));
    var p = NotebookService.passages(words);
    assertEquals(3, p.size(), "120-word windows every 90 words");
    assertTrue(p.stream().allMatch(x -> x.split(" ").length <= NotebookService.PASSAGE_WORDS));
  }
}
