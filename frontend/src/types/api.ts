export type Source = {
  title: string;
  url: string;
};

export type ChatResponse = {
  answer: string;
  sources: Source[];
};

export type Paper = {
  title: string;
  authors: string[];
  published_date: string;
  url: string;
  category: string;
};

export type PapersResponse = {
  papers: Paper[];
};

export type IngestResponse = {
  status: string;
  ingested_count: number;
  skipped_count: number;
};

export type PaperCategory = "cs.AI" | "cs.CL" | "cs.LG" | "cs.IR";
