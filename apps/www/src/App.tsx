import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event: React.changeEvent<HTMLInputElement>) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("❌ Veuillez sélectionner un fichier PDF !");
      return;
    }

    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://127.0.0.1:3000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setLoading(true);

      const pythonResponse = await axios.get("http://127.0.0.1:5000/date");
      setQuestions(pythonResponse.data.questions["pdf-file.pdf"]);

      setLoading(false);
    } catch (error) {
      setError("⚠️ Erreur lors de l'envoi du fichier. Veuillez réessayer !");
      console.error("Erreur :", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-200 to-blue-400 p-6">
      <div className="bg-white shadow-2xl rounded-2xl p-8 w-full max-w-lg">
        <h1 className="text-3xl font-bold text-gray-800 text-center mb-6">
          📄 Génération de Questions
        </h1>

        <div className="flex flex-col items-center space-y-4">
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="w-full border-2 border-gray-300 rounded-lg p-3 text-gray-700 bg-gray-50 
                        hover:bg-gray-100 transition duration-200 cursor-pointer"
          />

          <button
            onClick={handleUpload}
            className={`w-full py-3 rounded-lg font-bold text-white transition duration-300 ${
              loading
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 shadow-lg"
            }`}
          >
            {loading ? "⏳ Traitement..." : "📤 Uploader & Générer"}
          </button>
        </div>

        {error && (
          <p className="text-red-500 text-sm mt-4 text-center">{error}</p>
        )}

        {questions.length > 0 && (
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-gray-800">
              ✅ Questions Générées :
            </h2>
            <div className="mt-4 space-y-3">
              {questions.map((q, index) => (
                <div
                  key={index}
                  className="text-stone-700 bg-gray-100 p-4 rounded-lg shadow"
                >
                  {q}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
