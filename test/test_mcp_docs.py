"""
Tests for the developer documentation in mcpservice.py (get_doc, docs:// resources).

mcpservice.py runs in its own venv (venv/mcp). Run these tests with it:
    venv/mcp/bin/python -m unittest discover -v -s test -p 'test_mcp_docs.py'
With the restapi venv (no mcp package) the tests are skipped.
"""
import asyncio
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

try:
    import mcpservice
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:
    mcpservice = None

REPO_DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")


@unittest.skipIf(mcpservice is None, "mcp package not installed (use venv/mcp)")
class TestMcpDocs(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.docs = os.path.join(self.root, "docs")
        os.mkdir(self.docs)
        self._write("index.md", "# Index\n\n| [a.md](a.md) | A |\n| [link.md](link.md) | Symlink |\n"
                                "| [dir.md](dir.md) | Dir |\n| [fifo.md](fifo.md) | FIFO |\n| [big.md](big.md) | Big |\n"
                                "| [index.md](index.md) | self |\n")
        self._write("a.md", "# A\n")
        self._write("hidden.md", "# not in the index\n")
        with open(os.path.join(self.root, "secret.md"), "w") as f:
            f.write("secret\n")
        os.symlink(os.path.join(self.root, "secret.md"), os.path.join(self.docs, "link.md"))
        os.mkdir(os.path.join(self.docs, "dir.md"))
        os.mkfifo(os.path.join(self.docs, "fifo.md"))
        self._write("big.md", "x" * (mcpservice.DOCS_MAX_SIZE + 1))
        self._docs_dir = mcpservice.DOCS_DIR
        mcpservice.DOCS_DIR = self.docs

    def tearDown(self):
        mcpservice.DOCS_DIR = self._docs_dir
        shutil.rmtree(self.root)

    def _write(self, name, text):
        with open(os.path.join(self.docs, name), "w") as f:
            f.write(text)

    def _rejected(self, name):
        with self.assertRaises(ToolError, msg=repr(name)):
            mcpservice._read_doc(name)

    def test_000_index_and_document(self):
        self.assertTrue(mcpservice._read_doc().startswith("# Index"))
        self.assertTrue(mcpservice._read_doc("").startswith("# Index"))
        self.assertTrue(mcpservice._read_doc("index.md").startswith("# Index"))
        self.assertEqual(mcpservice._read_doc("a.md"), "# A\n")
        self.assertEqual(list(mcpservice._indexed_docs()), ["a.md", "link.md", "dir.md", "fifo.md", "big.md"])

    def test_001_names(self):
        for name in ("../secret.md", "../../etc/passwd", "/etc/passwd", "./a.md", "x/../a.md", "docs/a.md",
                     "a.md/", "a.md\n", "a.md\x00", "A.md", "a.MD", ".md", "a", "a.txt", "..",
                     "a.md/../a.md", "..\\secret.md", " a.md", "%2e%2e/secret.md"):
            self._rejected(name)
        for name in (1, ["a.md"], {"name": "a.md"}):
            self._rejected(name)

    def test_002_whitelist_and_file_type(self):
        self._rejected("hidden.md")     # exists, but not in the index
        self._rejected("missing.md")    # not in the index
        self._rejected("link.md")       # symlink to a file outside docs/
        self._rejected("dir.md")        # directory
        self._rejected("fifo.md")       # fifo, must not block
        self._rejected("big.md")        # too large

    def test_003_symlinked_index_and_missing_dir(self):
        os.remove(os.path.join(self.docs, "index.md"))
        os.symlink(os.path.join(self.root, "secret.md"), os.path.join(self.docs, "index.md"))
        self._rejected(None)
        mcpservice.DOCS_DIR = os.path.join(self.root, "missing")
        self._rejected(None)
        self._rejected("a.md")

    def test_004_tool_and_resources(self):
        async def run():
            result = await mcpservice.mcp.call_tool("get_doc", {"name": "a.md"})
            self.assertFalse(result.is_error)
            self.assertIn("# A", result.content[0].text)

            with self.assertRaises(ToolError):
                await mcpservice.mcp.call_tool("get_doc", {"name": "../secret.md"})

            mcpservice.load_doc_resources()
            uris = {str(r.uri) for r in await mcpservice.mcp.list_resources()}
            self.assertIn("docs://index.md", uris)
            self.assertIn("docs://a.md", uris)
            self.assertNotIn("docs://hidden.md", uris)

            contents = list(await mcpservice.mcp.read_resource("docs://a.md"))
            self.assertEqual(contents[0].content, "# A\n")
            for uri in ("docs://hidden.md", "docs://../secret.md", "docs://link.md"):
                with self.assertRaises(Exception, msg=uri):
                    list(await mcpservice.mcp.read_resource(uri))

            # documents removed from the index are removed from the resources
            self._write("index.md", "# Index\n")
            mcpservice.load_doc_resources()
            uris = {str(r.uri) for r in await mcpservice.mcp.list_resources()}
            self.assertEqual({u for u in uris if u.startswith("docs://")}, {"docs://index.md"})

        asyncio.run(run())

    def test_005_repository_docs(self):
        mcpservice.DOCS_DIR = REPO_DOCS
        docs = mcpservice._indexed_docs()
        self.assertIn("fetchxml.md", docs)
        for name in docs:
            self.assertTrue(mcpservice._read_doc(name).startswith("#"), name)
        if os.path.exists(os.path.join(REPO_DOCS, "server-ueberlast-2026-11-20.md")):
            self._rejected("server-ueberlast-2026-11-20.md")


if __name__ == "__main__":
    unittest.main()
