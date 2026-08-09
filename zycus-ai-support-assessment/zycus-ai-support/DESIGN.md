# Production Design Note

## Failure modes

The first production failure mode is incorrect ticket classification. A model can confuse issue categories or urgency, especially when a ticket contains multiple problems. I would detect this with an evaluation set covering each category and urgency level, monitor disagreement and low-confidence cases, and send uncertain tickets to human review. The evaluation harness in this project provides a small regression suite for this purpose.

The second failure mode is incorrect or missing knowledge-base retrieval. A generated answer can be plausible even when the retrieved documentation is unrelated. I would monitor retrieval scores, test known error-code cases, and require the final response to be grounded in retrieved documentation when a known issue is claimed. Exact error-code matching can also be added before semantic retrieval for high-value error codes.

The third failure mode is incorrect account-risk detection. An LLM may overstate a churn signal or invent evidence. The design therefore performs deterministic checks for account health, usage trend, P1 activity, escalation notes, and ticket language before generation. Ticket-based risk flags must contain a direct quote from the source ticket. Production monitoring would compare flagged risks against human TAM feedback.

## Latency versus quality

I chose a small local retrieval step followed by one LLM call for each user request. This keeps the pipeline simple while still giving the model relevant context. A larger retrieval corpus, multiple model calls, or an LLM judge would improve quality but increase latency and cost. If latency became the hard constraint, I would cache the knowledge-base index, reduce the number of retrieved chunks, use a smaller model for classification, and use deterministic rules for obvious error codes and urgency signals before calling the LLM.

## Data sensitivity

Ticket and account data can contain sensitive customer information. The system should send only the fields needed for the current task to an external model provider. Production data should be redacted or tokenised where possible, API keys must be stored in environment variables or a secret manager, and logs should avoid storing full ticket bodies or account records. The supplied assessment data is synthetic, but the same controls should apply to real customer data.

## Scaling

At ten times the current volume, the first limitations would be local file loading and repeated retrieval/index construction. The current 500-ticket dataset is small enough to process in memory, but a larger production system should move ticket and account data to a database and build the knowledge-base index once rather than on every process start. API workers can then share a persistent retrieval store, while asynchronous processing can be used for longer TAM summaries. Evaluation should run continuously in CI so prompt or model changes do not silently reduce quality.
