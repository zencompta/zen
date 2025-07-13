import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Upload,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react';

const AdvancedAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisType, setAnalysisType] = useState('auto');

  const analysisTypes = [
    { id: 'auto', name: 'Détection automatique', icon: Search },
    { id: 'ocr', name: 'Reconnaissance OCR', icon: Eye },
    { id: 'cross_validation', name: 'Validation croisée', icon: CheckCircle },
    { id: 'temporal', name: 'Analyse temporelle', icon: Clock },
    { id: 'suspicious', name: 'Détection d\'anomalies', icon: AlertTriangle }
  ];

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setAnalysisResults(null);
    }
  };

  const runAnalysis = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('analysis_type', analysisType);

      const response = await fetch('/api/advanced-analysis', {
        method: 'POST',
        body: formData
      });

      const results = await response.json();
      setAnalysisResults(results);
    } catch (error) {
      console.error('Erreur analyse:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const renderAnalysisResults = () => {
    if (!analysisResults) return null;

    return (
      <div className="mt-6 space-y-6">
        {/* Résumé de l'analyse */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-blue-600" />
            Résumé de l'analyse
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {analysisResults.summary?.valid_entries || 0}
              </div>
              <div className="text-sm text-green-700">Écritures valides</div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {analysisResults.summary?.warnings || 0}
              </div>
              <div className="text-sm text-yellow-700">Avertissements</div>
            </div>
            
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {analysisResults.summary?.errors || 0}
              </div>
              <div className="text-sm text-red-700">Erreurs détectées</div>
            </div>
          </div>
        </div>

        {/* Détection automatique du type */}
        {analysisResults.file_detection && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Search className="mr-2 h-5 w-5 text-blue-600" />
              Type de fichier détecté
            </h3>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="font-medium text-blue-900">
                {analysisResults.file_detection.type}
              </div>
              <div className="text-sm text-blue-700 mt-1">
                Confiance: {(analysisResults.file_detection.confidence * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-blue-600 mt-2">
                {analysisResults.file_detection.description}
              </div>
            </div>
          </div>
        )}

        {/* Résultats OCR */}
        {analysisResults.ocr_results && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Eye className="mr-2 h-5 w-5 text-blue-600" />
              Reconnaissance OCR
            </h3>
            
            <div className="space-y-3">
              <div className="text-sm text-gray-600">
                Texte extrait: {analysisResults.ocr_results.extracted_text?.length || 0} caractères
              </div>
              
              {analysisResults.ocr_results.structured_data && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Données structurées extraites:</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {Object.entries(analysisResults.ocr_results.structured_data).map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium">{key}:</span> {value}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Validation croisée */}
        {analysisResults.cross_validation && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <CheckCircle className="mr-2 h-5 w-5 text-blue-600" />
              Validation croisée
            </h3>
            
            <div className="space-y-3">
              {analysisResults.cross_validation.validations?.map((validation, index) => (
                <div key={index} className={`p-3 rounded-lg ${
                  validation.status === 'valid' ? 'bg-green-50 border border-green-200' :
                  validation.status === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                  'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{validation.rule}</span>
                    <span className={`text-sm px-2 py-1 rounded ${
                      validation.status === 'valid' ? 'bg-green-100 text-green-800' :
                      validation.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {validation.status}
                    </span>
                  </div>
                  {validation.message && (
                    <div className="text-sm text-gray-600 mt-1">{validation.message}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analyse temporelle */}
        {analysisResults.temporal_analysis && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Clock className="mr-2 h-5 w-5 text-blue-600" />
              Analyse de cohérence temporelle
            </h3>
            
            <div className="space-y-4">
              {analysisResults.temporal_analysis.anomalies?.map((anomaly, index) => (
                <div key={index} className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <div className="font-medium text-yellow-800">{anomaly.type}</div>
                  <div className="text-sm text-yellow-700 mt-1">{anomaly.description}</div>
                  <div className="text-xs text-yellow-600 mt-2">
                    Période: {anomaly.period} | Score: {anomaly.score}
                  </div>
                </div>
              ))}
              
              {(!analysisResults.temporal_analysis.anomalies || 
                analysisResults.temporal_analysis.anomalies.length === 0) && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <div className="text-green-800">Aucune anomalie temporelle détectée</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Écritures suspectes */}
        {analysisResults.suspicious_entries && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <AlertTriangle className="mr-2 h-5 w-5 text-red-600" />
              Écritures suspectes détectées
            </h3>
            
            <div className="space-y-3">
              {analysisResults.suspicious_entries.entries?.map((entry, index) => (
                <div key={index} className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-red-800">
                        Compte: {entry.account} | Montant: {entry.amount}€
                      </div>
                      <div className="text-sm text-red-700 mt-1">{entry.description}</div>
                      <div className="text-xs text-red-600 mt-2">
                        Raison: {entry.suspicion_reason}
                      </div>
                    </div>
                    <div className="text-sm font-medium text-red-600">
                      Score: {(entry.suspicion_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              ))}
              
              {(!analysisResults.suspicious_entries.entries || 
                analysisResults.suspicious_entries.entries.length === 0) && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <div className="text-green-800">Aucune écriture suspecte détectée</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Actions recommandées */}
        {analysisResults.recommendations && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Recommandations</h3>
            
            <div className="space-y-2">
              {analysisResults.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start">
                  <CheckCircle className="mr-2 h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{recommendation}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analyse Comptable Avancée
        </h1>
        <p className="text-gray-600">
          Utilisez l'intelligence artificielle pour analyser vos documents comptables
        </p>
      </div>

      {/* Configuration de l'analyse */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Configuration de l'analyse</h2>
        
        {/* Sélection du type d'analyse */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Type d'analyse
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {analysisTypes.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setAnalysisType(type.id)}
                  className={`p-3 rounded-lg border-2 transition-colors ${
                    analysisType === type.id
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-6 w-6 mx-auto mb-2" />
                  <div className="text-sm font-medium">{type.name}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Upload de fichier */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Document à analyser
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".pdf,.xlsx,.xls,.csv,.txt,.jpg,.png"
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="text-sm text-gray-600">
                {selectedFile ? (
                  <span className="font-medium text-blue-600">{selectedFile.name}</span>
                ) : (
                  <>
                    Cliquez pour sélectionner un fichier ou glissez-déposez
                    <br />
                    <span className="text-xs">PDF, Excel, CSV, Images acceptés</span>
                  </>
                )}
              </div>
            </label>
          </div>
        </div>

        {/* Bouton d'analyse */}
        <button
          onClick={runAnalysis}
          disabled={!selectedFile || isAnalyzing}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isAnalyzing ? (
            <>
              <RefreshCw className="animate-spin mr-2 h-4 w-4" />
              Analyse en cours...
            </>
          ) : (
            <>
              <Search className="mr-2 h-4 w-4" />
              Lancer l'analyse
            </>
          )}
        </button>
      </div>

      {/* Résultats de l'analyse */}
      {renderAnalysisResults()}
    </div>
  );
};

export default AdvancedAnalysis;

