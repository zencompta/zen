import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Target, 
  Lightbulb, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Settings,
  BarChart3,
  Zap,
  BookOpen,
  Download
} from 'lucide-react';

const AIFeatures = () => {
  const [activeTab, setActiveTab] = useState('classification');
  const [isTraining, setIsTraining] = useState(false);
  const [modelStats, setModelStats] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [learningProgress, setLearningProgress] = useState(null);

  const tabs = [
    { id: 'classification', name: 'Classification automatique', icon: Target },
    { id: 'anomaly', name: 'Détection d\'anomalies', icon: AlertCircle },
    { id: 'suggestions', name: 'Suggestions automatiques', icon: Lightbulb },
    { id: 'learning', name: 'Apprentissage adaptatif', icon: Brain }
  ];

  useEffect(() => {
    loadModelStats();
    loadPredictions();
    loadSuggestions();
  }, [activeTab]);

  const loadModelStats = async () => {
    try {
      const response = await fetch('/api/ai/model-stats');
      const stats = await response.json();
      setModelStats(stats);
    } catch (error) {
      console.error('Erreur chargement stats modèle:', error);
    }
  };

  const loadPredictions = async () => {
    try {
      const response = await fetch('/api/ai/predictions');
      const data = await response.json();
      setPredictions(data.predictions || []);
    } catch (error) {
      console.error('Erreur chargement prédictions:', error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const response = await fetch('/api/ai/suggestions');
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Erreur chargement suggestions:', error);
    }
  };

  const trainModel = async (modelType) => {
    setIsTraining(true);
    try {
      const response = await fetch('/api/ai/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_type: modelType })
      });
      
      const result = await response.json();
      if (result.success) {
        setLearningProgress(result.progress);
        loadModelStats();
      }
    } catch (error) {
      console.error('Erreur entraînement modèle:', error);
    } finally {
      setIsTraining(false);
    }
  };

  const renderClassificationTab = () => (
    <div className="space-y-6">
      {/* Statistiques du modèle */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <BarChart3 className="mr-2 h-5 w-5 text-blue-600" />
          Performance du modèle de classification
        </h3>
        
        {modelStats?.classification && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {(modelStats.classification.accuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-blue-700">Précision</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {modelStats.classification.total_predictions || 0}
              </div>
              <div className="text-sm text-green-700">Prédictions totales</div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {modelStats.classification.categories_learned || 0}
              </div>
              <div className="text-sm text-purple-700">Catégories apprises</div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {modelStats.classification.last_training || 'Jamais'}
              </div>
              <div className="text-sm text-orange-700">Dernier entraînement</div>
            </div>
          </div>
        )}
        
        <div className="mt-4">
          <button
            onClick={() => trainModel('classification')}
            disabled={isTraining}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            {isTraining ? (
              <>
                <RefreshCw className="animate-spin mr-2 h-4 w-4" />
                Entraînement en cours...
              </>
            ) : (
              <>
                <Zap className="mr-2 h-4 w-4" />
                Réentraîner le modèle
              </>
            )}
          </button>
        </div>
      </div>

      {/* Prédictions récentes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Classifications récentes</h3>
        
        <div className="space-y-3">
          {predictions.filter(p => p.type === 'classification').map((prediction, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium">{prediction.description}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    Compte suggéré: <span className="font-medium">{prediction.suggested_account}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(prediction.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm px-2 py-1 rounded ${
                    prediction.confidence > 0.8 ? 'bg-green-100 text-green-800' :
                    prediction.confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {(prediction.confidence * 100).toFixed(0)}% confiance
                  </div>
                  {prediction.user_validated && (
                    <CheckCircle className="h-4 w-4 text-green-600 mt-1 ml-auto" />
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {predictions.filter(p => p.type === 'classification').length === 0 && (
            <div className="text-center text-gray-500 py-8">
              Aucune classification récente
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderAnomalyTab = () => (
    <div className="space-y-6">
      {/* Statistiques de détection d'anomalies */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <AlertCircle className="mr-2 h-5 w-5 text-red-600" />
          Détection d'anomalies
        </h3>
        
        {modelStats?.anomaly && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {modelStats.anomaly.anomalies_detected || 0}
              </div>
              <div className="text-sm text-red-700">Anomalies détectées</div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {(modelStats.anomaly.false_positive_rate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-yellow-700">Taux de faux positifs</div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {(modelStats.anomaly.sensitivity * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-blue-700">Sensibilité</div>
            </div>
          </div>
        )}
      </div>

      {/* Anomalies détectées */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Anomalies récentes</h3>
        
        <div className="space-y-3">
          {predictions.filter(p => p.type === 'anomaly').map((anomaly, index) => (
            <div key={index} className={`border rounded-lg p-4 ${
              anomaly.severity === 'high' ? 'border-red-300 bg-red-50' :
              anomaly.severity === 'medium' ? 'border-yellow-300 bg-yellow-50' :
              'border-blue-300 bg-blue-50'
            }`}>
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium">{anomaly.description}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    Type: {anomaly.anomaly_type}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(anomaly.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm px-2 py-1 rounded ${
                    anomaly.severity === 'high' ? 'bg-red-100 text-red-800' :
                    anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {anomaly.severity}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Score: {(anomaly.anomaly_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
              
              {anomaly.recommendations && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-sm font-medium text-gray-700 mb-1">Recommandations:</div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {anomaly.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start">
                        <span className="mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
          
          {predictions.filter(p => p.type === 'anomaly').length === 0 && (
            <div className="text-center text-gray-500 py-8">
              Aucune anomalie détectée récemment
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderSuggestionsTab = () => (
    <div className="space-y-6">
      {/* Suggestions automatiques */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Lightbulb className="mr-2 h-5 w-5 text-yellow-600" />
          Suggestions automatiques
        </h3>
        
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <div className={`w-3 h-3 rounded-full mr-2 ${
                      suggestion.priority === 'high' ? 'bg-red-500' :
                      suggestion.priority === 'medium' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}></div>
                    <span className="font-medium">{suggestion.title}</span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    {suggestion.description}
                  </div>
                  
                  {suggestion.suggested_action && (
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-sm font-medium text-blue-800 mb-1">
                        Action suggérée:
                      </div>
                      <div className="text-sm text-blue-700">
                        {suggestion.suggested_action}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="ml-4 flex flex-col space-y-2">
                  <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                    Appliquer
                  </button>
                  <button className="bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400">
                    Ignorer
                  </button>
                </div>
              </div>
              
              {suggestion.impact && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-xs text-gray-500">
                    Impact estimé: {suggestion.impact}
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {suggestions.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              Aucune suggestion disponible
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderLearningTab = () => (
    <div className="space-y-6">
      {/* Apprentissage adaptatif */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Brain className="mr-2 h-5 w-5 text-purple-600" />
          Apprentissage adaptatif
        </h3>
        
        {learningProgress && (
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progression de l'apprentissage</span>
              <span>{learningProgress.percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${learningProgress.percentage}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {learningProgress.current_step} / {learningProgress.total_steps} étapes
            </div>
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Normes apprises */}
          <div>
            <h4 className="font-medium mb-3">Normes comptables apprises</h4>
            <div className="space-y-2">
              {['IFRS', 'SYSCOHADA', 'PCG France'].map((norm) => (
                <div key={norm} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm">{norm}</span>
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-1 mr-2">
                      <div className="bg-purple-600 h-1 rounded-full" style={{ width: '85%' }}></div>
                    </div>
                    <span className="text-xs text-gray-600">85%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Patterns reconnus */}
          <div>
            <h4 className="font-medium mb-3">Patterns reconnus</h4>
            <div className="space-y-2">
              {[
                { name: 'Écritures de vente', confidence: 92 },
                { name: 'Amortissements', confidence: 88 },
                { name: 'Provisions', confidence: 76 },
                { name: 'Régularisations', confidence: 84 }
              ].map((pattern) => (
                <div key={pattern.name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm">{pattern.name}</span>
                  <span className="text-xs text-gray-600">{pattern.confidence}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="font-medium mb-3">Actions d'apprentissage</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center justify-center">
              <BookOpen className="mr-2 h-4 w-4" />
              Apprendre nouvelles règles
            </button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center">
              <TrendingUp className="mr-2 h-4 w-4" />
              Optimiser modèles
            </button>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center justify-center">
              <Download className="mr-2 h-4 w-4" />
              Exporter modèles
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'classification':
        return renderClassificationTab();
      case 'anomaly':
        return renderAnomalyTab();
      case 'suggestions':
        return renderSuggestionsTab();
      case 'learning':
        return renderLearningTab();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Intelligence Artificielle
        </h1>
        <p className="text-gray-600">
          Exploitez la puissance de l'IA pour automatiser et optimiser vos processus comptables
        </p>
      </div>

      {/* Navigation par onglets */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Contenu de l'onglet actif */}
      {renderTabContent()}
    </div>
  );
};

export default AIFeatures;

