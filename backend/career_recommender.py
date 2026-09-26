RECOMMENDATION_DB = {
    "python": {
        "why_it_matters": "Python is a versatile and widely used language in backend development, data science, and automation.",
        "what_to_learn": ["Core syntax and data structures", "Object-oriented programming", "Package management (pip, virtual environments)"],
        "practice_idea": "Write a script to automate a daily task or parse a local file.",
        "project_idea": "Build a command-line tool or a simple REST API using a lightweight framework."
    },
    "fastapi": {
        "why_it_matters": "FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints.",
        "what_to_learn": ["Path and query parameters", "Pydantic models for data validation", "Dependency injection", "Asynchronous endpoints"],
        "practice_idea": "Create a single-endpoint API that returns mock data.",
        "project_idea": "Build a full CRUD API for a to-do list with a SQLite database."
    },
    "postgresql": {
        "why_it_matters": "PostgreSQL is a powerful, open-source object-relational database system.",
        "what_to_learn": ["Basic SQL queries (SELECT, INSERT, UPDATE, DELETE)", "Joins and subqueries", "Indexes and performance tuning"],
        "practice_idea": "Set up a local PostgreSQL server and create tables for a blog schema.",
        "project_idea": "Design and implement a normalized database for an e-commerce backend."
    },
    "rest api": {
        "why_it_matters": "REST APIs are the standard architectural style for providing interoperability between computer systems on the internet.",
        "what_to_learn": ["HTTP methods (GET, POST, PUT, DELETE)", "Status codes", "Statelessness and resource modeling", "Authentication (e.g., JWT)"],
        "practice_idea": "Consume a public REST API (like a weather API) and print the results.",
        "project_idea": "Build a fully compliant REST API with comprehensive endpoint testing."
    },
    "git": {
        "why_it_matters": "Git is the industry standard for version control, essential for collaborative software development.",
        "what_to_learn": ["Basic commands (clone, add, commit, push, pull)", "Branching and merging", "Resolving merge conflicts"],
        "practice_idea": "Create a local repository, make several commits on a separate branch, and merge it.",
        "project_idea": "Contribute to an open-source project on GitHub via a Pull Request."
    },
    "docker": {
        "why_it_matters": "Docker helps package applications and their dependencies into consistent environments.",
        "what_to_learn": ["Docker images and containers", "Dockerfile", "Docker Compose", "Container networking"],
        "practice_idea": "Containerize a simple Python script or Node.js app.",
        "project_idea": "Build and deploy a multi-container application (e.g., a web app and a database) using Docker Compose."
    },
    "java": {
        "why_it_matters": "Java is heavily used in enterprise applications and large-scale systems.",
        "what_to_learn": ["Object-oriented principles", "JVM basics", "Collections framework", "Concurrency"],
        "practice_idea": "Write a program that reads and processes a CSV file.",
        "project_idea": "Build a simple backend service using Spring Boot."
    },
    "javascript": {
        "why_it_matters": "JavaScript is the core language of the web, running in both browsers and servers.",
        "what_to_learn": ["ES6+ syntax", "DOM manipulation", "Promises and async/await", "Closures"],
        "practice_idea": "Build an interactive web page without any frameworks.",
        "project_idea": "Create a real-time chat application using JavaScript and WebSockets."
    },
    "typescript": {
        "why_it_matters": "TypeScript provides static typing over JavaScript, making large codebases much easier to maintain.",
        "what_to_learn": ["Types and interfaces", "Generics", "Type narrowing", "Configuring tsconfig.json"],
        "practice_idea": "Convert a small JavaScript script into TypeScript with strict type checking.",
        "project_idea": "Build a strongly-typed REST API using Node.js, Express, and TypeScript."
    },
    "react": {
        "why_it_matters": "React is a dominant library for building interactive user interfaces efficiently.",
        "what_to_learn": ["Components and props", "State management (useState, useReducer)", "Effects (useEffect)", "Context API"],
        "practice_idea": "Build a simple counter or a to-do list component.",
        "project_idea": "Create a dynamic, multi-page web application integrating with a public API."
    },
    "next.js": {
        "why_it_matters": "Next.js extends React by providing robust server-side rendering, routing, and full-stack capabilities.",
        "what_to_learn": ["App router and pages", "Server Components vs Client Components", "Data fetching", "API routes"],
        "practice_idea": "Create a static blog using Markdown files and Next.js static generation.",
        "project_idea": "Build a full-stack e-commerce storefront with server-side rendered product pages."
    },
    "node.js": {
        "why_it_matters": "Node.js allows developers to execute JavaScript on the server side, enabling unified full-stack development.",
        "what_to_learn": ["Event loop architecture", "NPM/Yarn", "File system and streams", "Creating web servers"],
        "practice_idea": "Build a basic HTTP server without using external frameworks.",
        "project_idea": "Develop a backend service with Express.js that interacts with a database."
    },
    "sql": {
        "why_it_matters": "SQL is the foundational language for managing and querying relational databases.",
        "what_to_learn": ["CRUD operations", "Aggregations (GROUP BY, HAVING)", "Joins", "Window functions"],
        "practice_idea": "Write queries to extract specific reporting data from a sample database.",
        "project_idea": "Design a relational schema for a library management system and write complex querying scripts."
    },
    "mysql": {
        "why_it_matters": "MySQL is one of the most popular open-source relational database management systems.",
        "what_to_learn": ["Table creation and data types", "Indexing strategies", "User privileges", "Storage engines"],
        "practice_idea": "Set up a local MySQL instance and import a sample dataset.",
        "project_idea": "Build a web application that securely stores user data in MySQL."
    },
    "oracle": {
        "why_it_matters": "Oracle Database is a powerful enterprise-grade relational database management system.",
        "what_to_learn": ["PL/SQL basics", "Oracle architecture", "Sequences and triggers", "Performance tuning"],
        "practice_idea": "Write a PL/SQL block that iterates over records and updates them conditionally.",
        "project_idea": "Design an enterprise schema with stored procedures for business logic."
    },
    "linux": {
        "why_it_matters": "Linux is the standard operating system for servers, cloud infrastructure, and deployment.",
        "what_to_learn": ["Command line navigation", "File permissions", "Process management", "Basic bash scripting"],
        "practice_idea": "Write a bash script to backup a specific directory every day.",
        "project_idea": "Set up a Virtual Private Server (VPS), configure a firewall, and deploy a web application."
    },
    "c++": {
        "why_it_matters": "C++ offers high performance and fine-grained control over system resources.",
        "what_to_learn": ["Pointers and memory management", "Object-oriented programming", "Standard Template Library (STL)", "Modern C++ features (smart pointers)"],
        "practice_idea": "Write a program that sorts a large dataset using STL algorithms.",
        "project_idea": "Develop a high-performance custom data structure or a basic game engine component."
    },
    "c": {
        "why_it_matters": "C provides low-level memory access and is foundational for operating systems and embedded systems.",
        "what_to_learn": ["Pointers and arrays", "Memory allocation (malloc/free)", "Structs", "File I/O"],
        "practice_idea": "Write a program that reads, manipulates, and saves binary files.",
        "project_idea": "Build a simple shell or a memory-efficient networking client."
    },
    "machine learning": {
        "why_it_matters": "Machine Learning enables systems to learn from data, powering modern AI applications.",
        "what_to_learn": ["Supervised vs unsupervised learning", "Model evaluation metrics", "Feature engineering", "Overfitting/underfitting"],
        "practice_idea": "Train a linear regression model on a standard dataset (like Housing Prices).",
        "project_idea": "Build an end-to-end ML pipeline that predicts customer churn and exposes it via an API."
    },
    "pytorch": {
        "why_it_matters": "PyTorch is a leading deep learning framework offering dynamic computation graphs and GPU acceleration.",
        "what_to_learn": ["Tensors and autograd", "Building neural networks (torch.nn)", "Training loops", "Dataset and DataLoader"],
        "practice_idea": "Implement a simple feedforward neural network for MNIST digit classification.",
        "project_idea": "Train and deploy an image classification or NLP model using PyTorch."
    },
    "hugging face": {
        "why_it_matters": "Hugging Face is the premier ecosystem for state-of-the-art NLP models (Transformers) and datasets.",
        "what_to_learn": ["Transformers library", "Tokenization", "Loading pre-trained models", "Fine-tuning pipelines"],
        "practice_idea": "Use a pre-trained model to perform sentiment analysis on text input.",
        "project_idea": "Fine-tune a large language model on a custom domain dataset."
    },
    "onnx runtime": {
        "why_it_matters": "ONNX Runtime accelerates machine learning inferencing across different hardware platforms.",
        "what_to_learn": ["Model export to ONNX format", "Inference session initialization", "Input/output binding", "Performance optimization options"],
        "practice_idea": "Export a PyTorch model to ONNX and run inference using ONNX Runtime in Python.",
        "project_idea": "Deploy an optimized machine learning model in a C++ or Node.js environment using ONNX Runtime."
    },
    "websockets": {
        "why_it_matters": "WebSockets enable full-duplex, real-time communication between clients and servers.",
        "what_to_learn": ["Connection handshake", "Event listeners", "Broadcasting messages", "Handling disconnections"],
        "practice_idea": "Create a simple echo server that sends back whatever the client transmits.",
        "project_idea": "Build a real-time collaborative document editor or chat room."
    },
    "redis": {
        "why_it_matters": "Redis is a blazing-fast in-memory data store heavily used for caching and message brokering.",
        "what_to_learn": ["Key-value operations", "Data types (Lists, Sets, Hashes)", "Expiration and TTL", "Pub/Sub mechanism"],
        "practice_idea": "Implement a simple cache wrapper for slow database queries.",
        "project_idea": "Build a real-time leader-board system or a rate-limiter using Redis."
    },
    "kubernetes": {
        "why_it_matters": "Kubernetes is the industry standard for container orchestration and automated scaling.",
        "what_to_learn": ["Pods and Deployments", "Services and Ingress", "ConfigMaps and Secrets", "kubectl commands"],
        "practice_idea": "Deploy a stateless Nginx container to a local Minikube cluster.",
        "project_idea": "Deploy a microservices architecture with load balancing and persistent storage on a Kubernetes cluster."
    }
}

GENERIC_RECOMMENDATION = {
    "why_it_matters": "This skill is relevant to the target job and was not found in the resume.",
    "what_to_learn": [
        "Core concepts",
        "Common tools and workflows",
        "Practical usage"
    ],
    "practice_idea": "Build a small practical project using this skill.",
    "project_idea": "Create a portfolio project that demonstrates practical use of this skill."
}

def generate_skill_recommendations(skill_gaps: list[dict]) -> dict:
    """
    Generate deterministic, actionable recommendations for each missing skill.
    """
    if not isinstance(skill_gaps, list):
        skill_gaps = []
        
    recommendations = []
    
    for gap in skill_gaps:
        if not isinstance(gap, dict):
            continue
            
        skill = gap.get("skill", "Unknown Skill")
        importance = gap.get("importance", "unknown")
        
        # Safely handle non-string skills
        if not isinstance(skill, str):
            skill = str(skill)
            
        skill_lower = skill.lower().strip()
        
        rec_data = RECOMMENDATION_DB.get(skill_lower, GENERIC_RECOMMENDATION)
        
        recommendations.append({
            "skill": skill,
            "importance": importance,
            "why_it_matters": rec_data["why_it_matters"],
            "what_to_learn": rec_data["what_to_learn"],
            "practice_idea": rec_data["practice_idea"],
            "project_idea": rec_data["project_idea"]
        })
        
    total = len(recommendations)
    
    if total == 0:
        summary = "No skill gaps were detected, so no additional skill recommendations are needed."
    else:
        summary = f"The candidate has {total} skill gap(s) that can be addressed through targeted learning and practice."
        
    return {
        "recommendations": recommendations,
        "total_recommendations": total,
        "summary": summary
    }
