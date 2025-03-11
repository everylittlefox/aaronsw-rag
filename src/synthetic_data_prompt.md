1. for the following interaction only respond with the instructed output and nothing more
2. a retrieval-augmented generation system based on the topic "Graphic Design" is to be be built
3. for the topic, you will generate questions a user might pose to the rag system
4. for each question, generate without repetition
   1. if the question is related to the topic,
      1. a list of text excerpts from documents that provide vital information to answering the question.
      2. a list of text excerpts from documents for which the relevant information is surrounded by noisy/less-important facts.
      3. a list of text excerpts from documents which are related to the topic but not to the question
   2. else, just a list of text excerpts from documents which are related to the topic but not to the question
5. each text excerpt should be at least 3 sentences long
6. the elements of each list should be related to the RAG topic in some way.
7. each list can contain 0 to 2 different elements
8. shuffle the order of the documents, so that the relevant documents aren't always the first
9. now, generate answers to the questions using only the relevant information contained in the list of texts. after each statement you make, reference the evident text document with its unique tag (in the form '<document-X>', where 'X' is the index of the text document in the combined list). the answers should not repeat the information in the documents but synthesize all the important facts into easy-to-understand sentences. remember, you found the documents; they weren't provided to you.
   1. do not make inferences or extrapolate. answer the questions based on the documents only. if the question cannot be answered with the information in the documents, say so.
   2. the documents were found by you after running some queries against a search engine. outside of the tagged references, do not make reference to them in any way.
   3. the generated answers should be straight to the point, well-structured, and referenced paragraphs.
   4. the answers to the questions should be in the style of literature reviews or summaries in the academic community. avoid being repetitive.
10. Remember, do not give an answer without references.
11. output in JSON format with the following fields: "question", "documents", "answer". the "documents" field should be a string: a concatenation of all the documents associated with a question (even the irrelevant ones) separated by new lines and a delimiter (‘\n---\n’) and start 'Document X:'. for now, output just one example.
    1.  remember to escape quotations in the JSON strings, but don't escape the '\n' character.
    2.  JSON strings do not allow for new lines. If you need to use new lines, use the newline character '\n'

example:
```json
{
        "question": "What are the regulations for hiking with dogs in national parks?",
        "documents": "Document 1: Shenandoah National Park is unique within the National Park System for its pet-friendly policies, allowing leashed dogs on 480 miles of trails including the Appalachian Trail within park boundaries. Dogs are prohibited only on 20 miles of specific trails where terrain is too dangerous or sensitive ecological areas exist. By contrast, nearby Great Smoky Mountains National Park prohibits dogs on all trails except for two short walking paths.\n---\nDocument 2: National Park Service regulations regarding dogs vary significantly between parks. Generally, dogs are prohibited on most trails within national parks to protect wildlife, natural resources, and other visitors' experiences. In parks where dogs are allowed on trails, they must be kept on leashes no longer than six feet at all times. Even in parks with strict trail limitations, dogs are typically permitted in developed areas such as campgrounds, picnic areas, and along roads.\n---\nDocument 3: Specific national parks with more permissive dog policies include Acadia National Park in Maine, which allows leashed dogs on most of its 100+ miles of hiking trails. The Cuyahoga Valley National Park in Ohio is similarly pet-friendly, permitting leashed dogs on all of its trails. However, even in these parks, dogs are not allowed in public buildings or on designated swimming beaches.\n---\nDocument 4: While national parks often have restrictive policies on dogs, national forests and Bureau of Land Management (BLM) lands typically allow dogs on most trails, though leash requirements vary by location. State parks fall somewhere in between, with policies determined by individual state park systems rather than federal regulations. These alternative public lands often provide comparable scenic experiences to national parks while offering more pet-friendly options.",
        "answer": "Dog regulations in national parks follow varied but generally restrictive policies. Most national parks prohibit dogs on trails to protect wildlife and natural resources, though they typically allow dogs in developed areas such as campgrounds, picnic grounds, and along roads, with mandatory six-foot leash requirements where permitted <document-2>. For more dog-friendly outdoor experiences, national forests and Bureau of Land Management lands offer wider trail access for pets, while state parks have intermediate policies determined at the state level <document-4>. Notable exceptions to restrictive national park policies include Acadia National Park (Maine) and Cuyahoga Valley National Park (Ohio), which allow leashed dogs on most or all trails, though prohibitions remain for public buildings and swimming beaches <document-3>. Shenandoah National Park stands out for permitting leashed dogs on 480 miles of trails including its Appalachian Trail sections, restricting dogs from only 20 miles of dangerous terrain or sensitive ecological areas <document-1>."
    }
```