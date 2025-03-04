1. for the following interaction only respond with the instructed output and nothing more
2. choose a topic based on which a retrieval-augmented generation system can be built
3. for the topic, generate a list of 10 questions a user might pose to a RAG system. 5 of these should be related to topic, 3 should only be weakly related, and the final two should be unrelated to the topic. number the questions from 1-10
4. for each question, generate without repetition
   1. if the question is related to the topic,
      1. a list of text excerpts from documents that provide vital information to answering the question.
      2. a list of text excerpts from documents for which the relevant information is surrounded by noisy/less-important facts.
   2. else, a list of text excerpts from documents which are related to the topic but not to the question
5. each text excerpt should be at least 3 sentences long
6. the elements of each list should be related to the RAG topic in some way.
7. each list can contain 0 to 2 different elements
8. now, generate answers to the questions using only the relevant information contained in the list of texts. after each statement you make, reference the evident text document with its unique tag (in the form '<document-X>', where 'X' is the index of the text document in the combined list). the answers should not repeat the information in the documents but synthesize all the important facts into easy-to-understand sentences. remember, you found the documents; they weren't provided to you.
   1. do not make inferences or extrapolate. answer the questions based on the documents only. if the question cannot be answered with the information in the documents, say so.
   2. the documents were found by you after running some queries against a search engine. outside of the tagged references, do not make reference to them in any way.
   3. the generated answers should be straight to the point, well-structured, and referenced paragraphs.
   4. the answers to the questions should be in the style of literature reviews or summaries in the academic community. avoid being repetitive.
9. Remember, do not give an answer without references.
10. output in JSON format with the following fields: "question", "documents", "answer". the "documents" field should be a string: a concatenation of all the documents associated with a question (even the irrelevant ones) separated by new lines and a delimiter (‘\n---\n’). for now, output just one example.
11. generate an example for a question that is unrelated to the topic
12. generate an example for a question with associated retrieved documents which do not provide sufficient information to give a definitive answer
13. now, generate another 15 examples, but this time, the questions are unrelated to the RAG topic. remember to follow the given instructions.