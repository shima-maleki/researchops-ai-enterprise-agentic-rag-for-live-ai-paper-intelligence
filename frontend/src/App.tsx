import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  ArrowUpRight,
  Bot,
  Database,
  Loader2,
  MessageSquare,
  Search,
  Send,
} from "lucide-react";
import {
  ingestPapers,
  searchPapers,
  streamChatMessage,
} from "./api/client";
import type { Paper, PaperCategory, Source } from "./types/api";

type View = "chat" | "papers";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

const categories: PaperCategory[] = ["cs.AI", "cs.CL", "cs.LG", "cs.IR"];

function App() {
  const [view, setView] = useState<View>("chat");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Ask about recent AI papers.",
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState<PaperCategory | "">("");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [papersLoading, setPapersLoading] = useState(false);
  const [papersError, setPapersError] = useState("");

  const [ingestLimit, setIngestLimit] = useState(100);
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestStatus, setIngestStatus] = useState("");

  const latestSources = useMemo(
    () =>
      messages
        .filter((message) => message.role === "assistant")
        .flatMap((message) => message.sources ?? [])
        .slice(-5),
    [messages],
  );

  useEffect(() => {
    void handlePaperSearch();
  }, []);

  async function handleChatSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = chatInput.trim();
    if (!message || chatLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };
    const assistantMessageId = crypto.randomUUID();
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      sources: [],
    };
    setMessages((current) => [...current, userMessage, assistantMessage]);
    setChatInput("");
    setChatLoading(true);
    setChatError("");

    try {
      await streamChatMessage(message, {
        onDelta: (content) => {
          setMessages((current) =>
            current.map((item) =>
              item.id === assistantMessageId
                ? { ...item, content: item.content + content }
                : item,
            ),
          );
        },
        onSources: (sources) => {
          setMessages((current) =>
            current.map((item) =>
              item.id === assistantMessageId ? { ...item, sources } : item,
            ),
          );
        },
      });
    } catch (error) {
      setChatError(error instanceof Error ? error.message : "Chat request failed");
      setMessages((current) =>
        current.filter((item) => item.id !== assistantMessageId),
      );
    } finally {
      setChatLoading(false);
    }
  }

  async function handlePaperSearch(event?: React.FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setPapersLoading(true);
    setPapersError("");

    try {
      const response = await searchPapers({
        keyword,
        category,
        limit: 50,
      });
      setPapers(response.papers);
    } catch (error) {
      setPapersError(error instanceof Error ? error.message : "Paper search failed");
    } finally {
      setPapersLoading(false);
    }
  }

  async function handleIngest() {
    setIngestLoading(true);
    setIngestStatus("");

    try {
      const response = await ingestPapers({
        limit: ingestLimit,
        categories,
      });
      setIngestStatus(
        `Ingested ${response.ingested_count}; skipped ${response.skipped_count}.`,
      );
      await handlePaperSearch();
    } catch (error) {
      setIngestStatus(error instanceof Error ? error.message : "Ingestion failed");
    } finally {
      setIngestLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Bot size={20} aria-hidden="true" />
          </div>
          <div>
            <h1>ResearchOps AI</h1>
            <p>Live AI paper intelligence</p>
          </div>
        </div>

        <nav className="nav-tabs" aria-label="Primary">
          <button
            className={view === "chat" ? "active" : ""}
            onClick={() => setView("chat")}
            type="button"
          >
            <MessageSquare size={16} aria-hidden="true" />
            Chat
          </button>
          <button
            className={view === "papers" ? "active" : ""}
            onClick={() => setView("papers")}
            type="button"
          >
            <Search size={16} aria-hidden="true" />
            Papers
          </button>
        </nav>

        <section className="ingest-panel" aria-label="Ingestion">
          <div className="field-row">
            <label htmlFor="ingest-limit">Limit</label>
            <input
              id="ingest-limit"
              min={1}
              max={500}
              onChange={(event) => setIngestLimit(Number(event.target.value))}
              type="number"
              value={ingestLimit}
            />
          </div>
          <button
            className="primary-button"
            disabled={ingestLoading}
            onClick={handleIngest}
            type="button"
          >
            {ingestLoading ? (
              <Loader2 className="spin" size={16} aria-hidden="true" />
            ) : (
              <Database size={16} aria-hidden="true" />
            )}
            Ingest
          </button>
          {ingestStatus && <p className="status-text">{ingestStatus}</p>}
        </section>
      </aside>

      <section className="workspace">
        {view === "chat" ? (
          <section className="chat-view" aria-label="Chat">
            <div className="chat-history">
              {messages.map((message) => (
                <article
                  className={`message ${message.role}`}
                  key={message.id}
                >
                  {message.role === "assistant" ? (
                    <div className="markdown-body">
                      {message.content ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        <Loader2 className="spin" size={16} aria-hidden="true" />
                      )}
                    </div>
                  ) : (
                    <p>{message.content}</p>
                  )}
                  {message.sources?.length ? (
                    <div className="source-list">
                      {message.sources.map((source) => (
                        <a
                          href={source.url}
                          key={source.url}
                          rel="noreferrer"
                          target="_blank"
                        >
                          {source.title}
                          <ArrowUpRight size={14} aria-hidden="true" />
                        </a>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>

            {chatError && <p className="error-text">{chatError}</p>}

            <form className="composer" onSubmit={handleChatSubmit}>
              <input
                aria-label="Message"
                onChange={(event) => setChatInput(event.target.value)}
                placeholder="Ask about agentic RAG, language agents, or vector search"
                value={chatInput}
              />
              <button
                className="icon-button"
                disabled={chatLoading}
                title="Send"
                type="submit"
              >
                <Send size={18} aria-hidden="true" />
              </button>
            </form>
          </section>
        ) : (
          <section className="papers-view" aria-label="Papers">
            <form className="search-bar" onSubmit={handlePaperSearch}>
              <div className="search-input">
                <Search size={17} aria-hidden="true" />
                <input
                  aria-label="Keyword"
                  onChange={(event) => setKeyword(event.target.value)}
                  placeholder="Search papers"
                  value={keyword}
                />
              </div>
              <select
                aria-label="Category"
                onChange={(event) =>
                  setCategory(event.target.value as PaperCategory | "")
                }
                value={category}
              >
                <option value="">All categories</option>
                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
              <button className="primary-button" disabled={papersLoading}>
                {papersLoading ? (
                  <Loader2 className="spin" size={16} aria-hidden="true" />
                ) : (
                  <Search size={16} aria-hidden="true" />
                )}
                Search
              </button>
            </form>

            {papersError && <p className="error-text">{papersError}</p>}

            <div className="paper-list">
              {papers.map((paper) => (
                <article className="paper-card" key={`${paper.url}-${paper.title}`}>
                  <div>
                    <span className="category-pill">{paper.category}</span>
                    <h2>{paper.title}</h2>
                  </div>
                  <p>{paper.authors.join(", ")}</p>
                  <div className="paper-meta">
                    <span>{paper.published_date}</span>
                    <a href={paper.url} rel="noreferrer" target="_blank">
                      PDF
                      <ArrowUpRight size={14} aria-hidden="true" />
                    </a>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>

      <aside className="sources-panel" aria-label="Sources">
        <h2>Sources</h2>
        {latestSources.length ? (
          latestSources.map((source) => (
            <a href={source.url} key={source.url} rel="noreferrer" target="_blank">
              {source.title}
              <ArrowUpRight size={14} aria-hidden="true" />
            </a>
          ))
        ) : (
          <p>No sources yet.</p>
        )}
      </aside>
    </main>
  );
}

export default App;
