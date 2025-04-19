# Interview Eval

Interview Eval is an AI-powered platform that uses Retrieval-Augmented Generation (RAG) to revolutionize the interview evaluation process. It takes interview feedback as input, extracts relevant information, and generates constructive feedback based on structured data. By leveraging the power of Gen AI and natural language processing, Interview Eval helps hiring managers and recruiters streamline their evaluation process, reduce bias, and make more informed hiring decisions.

## Features

- **RAG Integration**: Uses retrieval-augmented generation to provide insightful feedback.
- **PDF to JSON Conversion**: Converts interview feedback PDFs to JSON format for easy processing.
- **Prompt Rendering**: Utilizes Jinja2 templates for dynamic prompt rendering.
- **Vector Database**: Employs FAISS for efficient interview question retrieval.
- **Dockerized Services**: Each component runs in its own Docker container for modularity and scalability.

## Project Structure

- `Dockerfile.*`: Docker configurations for different services.
- `requirements.txt`: Lists all Python dependencies.
- `vectordb.py`: Handles vector database operations using FAISS.
- `ws_*`: Flask-based web services for different functionalities.
- `promptRenderer.py`: Renders prompts using Jinja2 templates.
- `pdf_to_json.py`: Converts PDF files to JSON format.
- `docs/`: Contains supporting documents and templates.
- `test/`: Directory for unit and integration tests.
- `manage_services.sh`: Script for managing services.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd interview-eval
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Build Docker images**:
   ```bash
   ./build.sh
   ```

## Usage

1. **Start the services**:
   ```bash
   docker-compose up
   ```

2. **Access the services**:
   - PDF to JSON Service: `http://localhost:5002`
   - Interview Copilot Service: `http://localhost:5003`
   - Prompt Renderer Service: `http://localhost:5001`
   - Vector Search Service: `http://localhost:5000`

3. **API Endpoints**:
   - `/upload`: Upload PDF for conversion.
   - `/search`: Search for interview questions.
   - `/render`: Render prompts using templates.
   - `/copilot`: Process queries with the Interview Copilot.

## Service Management

The `manage_services.sh` script is a utility for managing the various services within the Interview Eval project. It provides a command-line interface to start, stop, restart, and check the status of the services. It also allows you to tail the logs for all services. This is especially usedful while you are developing and making local changes that you want to be hotloaded.

### Key Features

- **Service Management**: Start, stop, and restart services using simple commands.
- **Environment Verification**: Checks if the virtual environment and required packages are set up correctly.
- **Logging**: Consolidates logs for all services into a single file.
- **Service Status**: Provides the status of each service.

### Usage

- **Start Services**: 
  ```bash
  ./manage_services.sh start [service_name]
  ```
  If no `service_name` is provided, all services will be started.

- **Stop Services**: 
  ```bash
  ./manage_services.sh stop [service_name]
  ```
  If no `service_name` is provided, all services will be stopped.

- **Restart Services**: 
  ```bash
  ./manage_services.sh restart [service_name]
  ```
  If no `service_name` is provided, all services will be restarted.

- **Check Status**: 
  ```bash
  ./manage_services.sh status [service_name]
  ```
  If no `service_name` is provided, the status of all services will be displayed.

- **Tail Logs**: 
  ```bash
  ./manage_services.sh logs
  ```

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request for review.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact [ateja at gmail.com].
