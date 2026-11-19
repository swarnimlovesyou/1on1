/* Runs learner Python with Pyodide (CPython compiled to WebAssembly) off the page's main thread.
   Used only for ungraded "Run" when no server runner is configured; official grading stays on the server. */
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
importScripts(PYODIDE + "pyodide.js");

const ready = loadPyodide({ indexURL: PYODIDE }).then((py) => {
  self.postMessage({ type: "ready" });
  return py;
});

const HARNESS = `
import sys, io, traceback
sys.stdin = io.StringIO(__stdin)
__out, __err = io.StringIO(), io.StringIO()
sys.stdout, sys.stderr = __out, __err
try:
    exec(compile(__src, "main.py", "exec"), {"__name__": "__main__"})
except SystemExit:
    pass
except BaseException:
    traceback.print_exc()
finally:
    sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
`;

self.onmessage = async (event) => {
  const { code, input } = event.data;
  try {
    const py = await ready;
    py.globals.set("__src", code);
    py.globals.set("__stdin", input);
    const started = performance.now();
    py.runPython(HARNESS);
    const ms = performance.now() - started;
    self.postMessage({ type: "done", stdout: py.globals.get("__out").getvalue(), stderr: py.globals.get("__err").getvalue(), ms });
  } catch (error) {
    self.postMessage({ type: "done", stdout: "", stderr: String(error), ms: 0 });
  }
};
