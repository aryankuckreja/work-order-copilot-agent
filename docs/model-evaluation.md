# Model evaluation

The agent's answers drive real work orders, which makes a confident wrong answer worse than no answer. Models were compared on the same scripted test conversations before one was chosen.

## Method

- Fixed test cases covering common customers, thin-history customers, ambiguous markup, and messy site names.
- Every answer checked against the source data for the numbers it quoted.
- Pass criteria: correct field values, correct confidence wording, and no invented numbers.

## Outcome

- Three models were compared.
- One model **fabricated a markup rate** that did not exist in the data during testing and was rejected, even though its answers read well.
- The chosen model stayed grounded in the tool results and said when data was insufficient.

## Lessons

- Test for fabrication explicitly: ask questions where the honest answer is "not enough history".
- Prefer returning distributions (counts and shares) from tools over single values, which gives the model less room to invent.
