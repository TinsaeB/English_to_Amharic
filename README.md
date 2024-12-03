# English to Amharic PDF Translator

A powerful web application that translates PDF documents from English to Amharic using advanced machine learning techniques. Built with Streamlit and Facebook's NLLB (No Language Left Behind) model.

## 🌟 Features

- **PDF Document Translation**: Translate entire PDF documents while preserving layout
- **Smart Text Detection**: Automatically detects and processes text content in PDFs
- **Layout Preservation**: Maintains original document formatting and positioning
- **Unicode Support**: Full support for Amharic Unicode characters
- **Robust Error Handling**: Graceful handling of various PDF formats and structures
- **Progress Tracking**: Real-time translation progress indicators
- **Modern UI**: Clean and intuitive interface built with Streamlit

## 🔧 Technical Stack

- **Python**: 3.10
- **Frontend**: Streamlit
- **PDF Processing**: ReportLab, PyPDF2
- **Translation**: Transformers (NLLB model)
- **Font Support**: Nyala (Amharic)

## 📋 Requirements

- Python 3.10
- Miniconda/Anaconda (recommended)
- 2GB+ free disk space (for model and dependencies)
- 8GB+ RAM recommended

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/English_to_Amharic.git
cd English_to_Amharic
```

2. Create and activate the conda environment:
```bash
conda create -n amharic_translator python=3.10
conda activate amharic_translator
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Start the application:
```bash
run.bat
```

2. Open your web browser and navigate to:
```
http://localhost:8502
```

3. Using the application:
   - Click "Upload PDF" to select your English PDF document
   - Wait for the translation process to complete
   - Download the translated Amharic PDF

## 🔍 Important Notes

- First run will download the translation model (~1.2GB)
- Translation time depends on document size and complexity
- Supported input formats: PDF files
- Internet connection required for first-time model download
- Temporary files are automatically cleaned up

## 🛠️ Technical Details

- Uses NLLB-200 model for high-quality translations
- Implements custom PDF handling for Amharic text
- Includes font fallback mechanisms
- Preserves original document structure
- Handles Unicode encoding for Amharic script

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Known Limitations

- Large PDFs may require significant processing time
- Some complex PDF layouts might need manual adjustment
- Memory usage increases with document size
