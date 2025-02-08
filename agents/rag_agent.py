from termcolor import colored

from agents.agent_master import Agent
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from prompts.ragagent_prompt import ragagent_prompt


class RAGAgent(Agent):
    def invoke(self, research_question, vector_db_dir, API_key, prompt=ragagent_prompt, feedback=None):

        # use the same as used in creating vectorDB
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'mps'}
        encode_kwargs = {'normalize_embeddings': False}
        model = HuggingFaceEmbeddings(
            multi_process=False, # to run on multiple GPUs
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        vectordb = Chroma(persist_directory=vector_db_dir, embedding_function=model)
        retriever = vectordb.as_retriever(search_kwargs={"k": 1, "fetch_k": 5})

        # retrieve the relevant documents
        relevant_docs = retriever.get_relevant_documents(research_question)

        # Generate response
        
        llm = self.get_llm()

        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        rag_prompt = prompt.format(context=context)
        messages = [
            {"role": "system", "content": rag_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]
        response = llm.invoke(messages).content

        print(colored(f"RAG Agent👩🏿‍💻  answers :  {response}", 'yellow'))

        self.update_state("ragagent_response", response)
        return self.state