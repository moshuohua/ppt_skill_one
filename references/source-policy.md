# Source policy

## Source mix

For a normal AI or cloud insight page, use:

1. At least one primary source for the core fact or number.
2. One to three independent global AI media, analyst, or author-led blog conclusions when relevant.
3. A transparent research or consulting source when it provides useful comparable data.

Primary sources include official documentation, company blogs, release notes, papers, financial reports, regulatory filings, and original datasets.

Independent interpretation may come from established outlets or author-led publications with a visible author, date, original reasoning, and evidence. Useful examples include MIT Technology Review, IEEE Spectrum, The Batch, Import AI, Latent Space, Interconnects, SemiAnalysis, The Gradient, AI Snake Oil, Simon Willison, Lilian Weng, Benedict Evans, and Stratechery. This is a quality guide, not a mandatory whitelist. Choose the source that directly addresses the claim.

## How to use media and blogs

- Use them for interpretation, not as a substitute for the original number.
- Paraphrase the useful conclusion in plain Chinese.
- Do not copy a long passage.
- Check whether later evidence changed the conclusion.
- Attribute a strong opinion to its author instead of presenting it as settled fact.

## Verification record

For every source, record:

- source id;
- institution or author;
- title;
- publication date;
- access date;
- URL;
- source type;
- exact claim or chart it supports;
- metric definition, unit, period, and scope when numeric.

Use a current `as_of_date`. For fast-moving AI topics, prioritize material from the last three to six months. Older evidence is acceptable only when it is still authoritative and its continued relevance is checked.

## Conflict handling

When figures disagree:

1. Compare definitions, time windows, units, geography, and sample.
2. Prefer the original and more recent source with a clear method.
3. Do not average incompatible figures.
4. State the range or uncertainty if the difference matters.

## Slide and notes

Put complete citations and URLs in speaker notes under a literal `[Sources]` heading. Every externally sourced non-trivial claim and asset must be traceable there.

A visible source footer is optional. Use it only when the audience benefits from seeing provenance on the page. When used:

- show two to four concise source labels without long URLs;
- keep it on one line;
- place its left and bottom edges exactly 30 pt from the slide edges;
- use `Microsoft YaHei`, 10 pt, italic, `#8C8C8C`, left aligned;
- do not place any other footnote or caveat in the title region.

## Evidence language

- State a verified fact directly and cite its source.
- Attribute an external interpretation to the institution or author.
- Introduce an author inference with language such as `我们的判断` or make the inferential step explicit in the surrounding logic.
- Preserve important uncertainty in notes when it would overload the page.
