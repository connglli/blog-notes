# Blogs and Notes

> [!NOTE]
> 
> For blogs newer than 2026/10/01, I'll make each of them a Markdown file. Old blogs stay in Issues.

This is a collection of my own blogs and notes (goto any Markdown or [Issues](https://github.com/connglli/blog-notes/issues)). Opinions are also my own. Or check out [my website](https://connglli.github.io).

### 🤖 Agents

This repo is now assisted by agents. I collect papers, blogs, projects, etc. that I'm interested in and ask agents to summarize them into a blog. Every new blog gets one Markdown file named after it, and each file is self-contained:
+ the key insight,
+ the basic idea,
+ an illustrative example,
+ and the concepts and terms needed to follow it.

Start each summary from [TEMPLATE.md](TEMPLATE.md); the writing and source-review rules live in [AGENTS.md](AGENTS.md). Keep one bare publication URL and no direct PDF links. Code, documentation, and artifact links may use descriptive labels.

Enable the pre-commit format check once per clone (Python 3.10+ and Git are required):

```sh
git config --local core.hooksPath .githooks
```

The hook and `python3 scripts/check_summaries.py` check only staged changes by default, using file contents and `TEMPLATE.md` from the index. Unchanged files, deletions, unstaged changes, and untracked drafts are excluded. An explicit `--no-staged` checks the working tree, including untracked drafts. To run the checker tests, use `python3 -m unittest discover -s scripts -p 'test_*.py'`. Technical accuracy still requires checking the original source. Repository documentation and the reading list in `paper.md` are exempt from the summary template.

### 🏡 Topics

Topics are various:
+ `compilers` and `virtual machines`,
+ `software/systems verification` and programming languages
+ `ai agents`, `reasoning`, and language models,
+ `android` and `aosp`,
+ `browsers` and `web`,
+ and other miscellaneous ones.

### 🚦Attention

You'd better know before reading them,
+ Some of them are accomplished, but some are not (they are tagged with `todo` in Issues; for these, I either know little about them, or not well prepared to write them down in a logical and structural manner)
+ Some of them are my personal thoughts, but some of them are learned or borrowed directly from others (but I've put references)
+ Some of them are summarized by agents; I'll read them before releasing them but there may still be errors
+ Take your own risk

### 🤝 Welcome

Last but not least, I'm learning as you are. So discussions are very much welcome. Let me know if you have any comments, suggestions, questions, or even **corrections**. Please directly make comments under the issues that you are interested.
