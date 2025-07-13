import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  FileText,
  Settings,
  Bell,
  TrendingUp,
  Filter,
  Download,
  RefreshCw,
  Eye,
  X,
  Check
} from 'lucide-react';

const ComplianceCenter = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedStandard, setSelectedStandard] = useState('ifrs');
  const [complianceData, setComplianceData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [checklist, setChecklist] = useState(null);
  const [isValidating, setIsValidating] = useState(false);

  const tabs = [
    { id: 'overview', name: 'Vue d\'ensemble', icon: TrendingUp },
    { id: 'validation', name: 'Validation', icon: CheckCircle },
    { id: 'checklist', name: 'Check-lists', icon: FileText },
    { id: 'alerts', name: 'Alertes', icon: Bell },
    { id: 'settings', name: 'Configuration', icon: Settings }
  ];

  const standards = [
    { id: 'ifrs', name: 'IFRS', description: 'Normes internationales' },
    { id: 'syscohada', name: 'SYSCOHADA', description: 'Normes OHADA' },
    { id: 'french_gaap', name: 'PCG France', description: 'Plan comptable général français' },
    { id: 'us_gaap', name: 'US GAAP', description: 'Normes américaines' }
  ];

  useEffect(() => {
    loadComplianceData();
    loadAlerts();
    loadChecklist();
  }, [selectedStandard]);

  const loadComplianceData = async () => {
    try {
      const response = await fetch(`/api/compliance/overview?standard=${selectedStandard}`);
      const data = await response.json();
      setComplianceData(data);
    } catch (error) {
      console.error('Erreur chargement données conformité:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await fetch('/api/compliance/alerts');
      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (error) {
      console.error('Erreur chargement alertes:', error);
    }
  };

  const loadChecklist = async () => {
    try {
      const response = await fetch(`/api/compliance/checklist?standard=${selectedStandard}`);
      const data = await response.json();
      setChecklist(data);
    } catch (error) {
      console.error('Erreur chargement checklist:', error);
    }
  };

  const runValidation = async () => {
    setIsValidating(true);
    try {
      const response = await fetch('/api/compliance/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ standard: selectedStandard })
      });
      
      const result = await response.json();
      setComplianceData(result);
      loadAlerts();
    } catch (error) {
      console.error('Erreur validation:', error);
    } finally {
      setIsValidating(false);
    }
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Score de conformité */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Shield className="mr-2 h-5 w-5 text-blue-600" />
          Score de conformité {standards.find(s => s.id === selectedStandard)?.name}
        </h3>
        
        {complianceData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`text-4xl font-bold mb-2 ${
                complianceData.compliance_score >= 0.9 ? 'text-green-600' :
                complianceData.compliance_score >= 0.7 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {(complianceData.compliance_score * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600">Score global</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">
                {complianceData.validation_summary?.total_rules_checked || 0}
              </div>
              <div className="text-sm text-gray-600">Règles vérifiées</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600 mb-2">
                {complianceData.validation_summary?.violations_found || 0}
              </div>
              <div className="text-sm text-gray-600">Violations détectées</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600 mb-2">
                {complianceData.processing_time?.toFixed(2) || 0}s
              </div>
              <div className="text-sm text-gray-600">Temps de traitement</div>
            </div>
          </div>
        )}
      </div>

      {/* Répartition des violations par sévérité */}
      {complianceData?.validation_summary?.severity_distribution && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Répartition des violations</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {complianceData.validation_summary.severity_distribution.critical || 0}
              </div>
              <div className="text-sm text-red-700">Critiques</div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {complianceData.validation_summary.severity_distribution.error || 0}
              </div>
              <div className="text-sm text-orange-700">Erreurs</div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {complianceData.validation_summary.severity_distribution.warning || 0}
              </div>
              <div className="text-sm text-yellow-700">Avertissements</div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {complianceData.validation_summary.severity_distribution.info || 0}
              </div>
              <div className="text-sm text-blue-700">Informations</div>
            </div>
          </div>
        </div>
      )}

      {/* Recommandations */}
      {complianceData?.recommendations && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recommandations</h3>
          
          <div className="space-y-3">
            {complianceData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                <CheckCircle className="mr-3 h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-blue-800">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderValidationTab = () => (
    <div className="space-y-6">
      {/* Contrôles de validation */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Validation de conformité</h3>
          <button
            onClick={runValidation}
            disabled={isValidating}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            {isValidating ? (
              <>
                <RefreshCw className="animate-spin mr-2 h-4 w-4" />
                Validation en cours...
              </>
            ) : (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Lancer la validation
              </>
            )}
          </button>
        </div>
        
        <div className="text-sm text-gray-600 mb-4">
          Norme sélectionnée: <span className="font-medium">{standards.find(s => s.id === selectedStandard)?.name}</span>
        </div>
      </div>

      {/* Résultats de validation */}
      {complianceData?.violations && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Violations détectées</h3>
          
          <div className="space-y-4">
            {complianceData.violations.map((violation, index) => (
              <div key={index} className={`border rounded-lg p-4 ${
                violation.severity === 'critical' ? 'border-red-300 bg-red-50' :
                violation.severity === 'error' ? 'border-orange-300 bg-orange-50' :
                violation.severity === 'warning' ? 'border-yellow-300 bg-yellow-50' :
                'border-blue-300 bg-blue-50'
              }`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <AlertTriangle className={`mr-2 h-4 w-4 ${
                        violation.severity === 'critical' ? 'text-red-600' :
                        violation.severity === 'error' ? 'text-orange-600' :
                        violation.severity === 'warning' ? 'text-yellow-600' :
                        'text-blue-600'
                      }`} />
                      <span className="font-medium">{violation.title}</span>
                    </div>
                    
                    <div className="text-sm text-gray-700 mb-2">
                      {violation.description}
                    </div>
                    
                    {violation.affected_entries?.length > 0 && (
                      <div className="text-xs text-gray-600 mb-2">
                        Écritures affectées: {violation.affected_entries.join(', ')}
                      </div>
                    )}
                    
                    {violation.remediation_steps?.length > 0 && (
                      <div className="mt-3">
                        <div className="text-sm font-medium text-gray-700 mb-1">
                          Actions correctives:
                        </div>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {violation.remediation_steps.map((step, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2">•</span>
                              {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4">
                    <span className={`text-xs px-2 py-1 rounded ${
                      violation.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      violation.severity === 'error' ? 'bg-orange-100 text-orange-800' :
                      violation.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {violation.severity}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            
            {complianceData.violations.length === 0 && (
              <div className="text-center text-green-600 py-8">
                <CheckCircle className="h-12 w-12 mx-auto mb-4" />
                <div className="font-medium">Aucune violation détectée</div>
                <div className="text-sm">Votre comptabilité est conforme à la norme {standards.find(s => s.id === selectedStandard)?.name}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderChecklistTab = () => (
    <div className="space-y-6">
      {/* Check-list de conformité */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">
            Check-list {standards.find(s => s.id === selectedStandard)?.name}
          </h3>
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center">
            <Download className="mr-2 h-4 w-4" />
            Exporter
          </button>
        </div>
        
        {checklist?.categories && Object.entries(checklist.categories).map(([category, items]) => (
          <div key={category} className="mb-6">
            <h4 className="font-medium text-gray-900 mb-3 capitalize">
              {category.replace('_', ' ')}
            </h4>
            
            <div className="space-y-2">
              {items.map((item, index) => (
                <div key={index} className="flex items-start p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center mr-3">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 rounded"
                      defaultChecked={item.status === 'completed'}
                    />
                  </div>
                  
                  <div className="flex-1">
                    <div className="font-medium text-sm">{item.title}</div>
                    <div className="text-xs text-gray-600 mt-1">{item.description}</div>
                    
                    {item.references?.length > 0 && (
                      <div className="text-xs text-blue-600 mt-2">
                        Références: {item.references.join(', ')}
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4">
                    <span className={`text-xs px-2 py-1 rounded ${
                      item.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      item.severity === 'error' ? 'bg-orange-100 text-orange-800' :
                      item.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {item.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
        
        {checklist?.total_items && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              Total: {checklist.total_items} éléments
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderAlertsTab = () => (
    <div className="space-y-6">
      {/* Filtres d'alertes */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Alertes de conformité</h3>
          <div className="flex space-x-2">
            <button className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 flex items-center">
              <Filter className="mr-2 h-4 w-4" />
              Filtrer
            </button>
            <button className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 flex items-center">
              <RefreshCw className="mr-2 h-4 w-4" />
              Actualiser
            </button>
          </div>
        </div>
      </div>

      {/* Liste des alertes */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-4">
          {alerts.map((alert, index) => (
            <div key={index} className={`border rounded-lg p-4 ${
              alert.priority === 'critical' ? 'border-red-300 bg-red-50' :
              alert.priority === 'high' ? 'border-orange-300 bg-orange-50' :
              alert.priority === 'medium' ? 'border-yellow-300 bg-yellow-50' :
              'border-blue-300 bg-blue-50'
            }`}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <Bell className={`mr-2 h-4 w-4 ${
                      alert.priority === 'critical' ? 'text-red-600' :
                      alert.priority === 'high' ? 'text-orange-600' :
                      alert.priority === 'medium' ? 'text-yellow-600' :
                      'text-blue-600'
                    }`} />
                    <span className="font-medium">{alert.title}</span>
                    <span className={`ml-2 text-xs px-2 py-1 rounded ${
                      alert.status === 'active' ? 'bg-red-100 text-red-800' :
                      alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {alert.status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-700 mb-2">
                    {alert.description}
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    {new Date(alert.created_at).toLocaleString()}
                    {alert.due_date && (
                      <span className="ml-4">
                        Échéance: {new Date(alert.due_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="ml-4 flex space-x-2">
                  <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                    <Eye className="h-3 w-3" />
                  </button>
                  <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                    <Check className="h-3 w-3" />
                  </button>
                  <button className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700">
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          {alerts.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <Bell className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <div>Aucune alerte active</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="space-y-6">
      {/* Configuration des normes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Configuration des normes</h3>
        
        <div className="space-y-4">
          {standards.map((standard) => (
            <div key={standard.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <div className="font-medium">{standard.name}</div>
                <div className="text-sm text-gray-600">{standard.description}</div>
              </div>
              <div className="flex items-center space-x-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 rounded"
                    defaultChecked={standard.id === selectedStandard}
                  />
                  <span className="ml-2 text-sm">Actif</span>
                </label>
                <button className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200">
                  Configurer
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Configuration des alertes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Configuration des alertes</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Alertes en temps réel</div>
              <div className="text-sm text-gray-600">Recevoir des alertes lors de la saisie</div>
            </div>
            <label className="flex items-center">
              <input type="checkbox" className="h-4 w-4 text-blue-600 rounded" defaultChecked />
              <span className="ml-2 text-sm">Activé</span>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Notifications par email</div>
              <div className="text-sm text-gray-600">Recevoir les alertes par email</div>
            </div>
            <label className="flex items-center">
              <input type="checkbox" className="h-4 w-4 text-blue-600 rounded" />
              <span className="ml-2 text-sm">Activé</span>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Validation automatique</div>
              <div className="text-sm text-gray-600">Valider automatiquement à la clôture</div>
            </div>
            <label className="flex items-center">
              <input type="checkbox" className="h-4 w-4 text-blue-600 rounded" defaultChecked />
              <span className="ml-2 text-sm">Activé</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverviewTab();
      case 'validation':
        return renderValidationTab();
      case 'checklist':
        return renderChecklistTab();
      case 'alerts':
        return renderAlertsTab();
      case 'settings':
        return renderSettingsTab();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Centre de Conformité Réglementaire
        </h1>
        <p className="text-gray-600">
          Assurez la conformité de votre comptabilité aux normes réglementaires
        </p>
      </div>

      {/* Sélection de la norme */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Norme comptable</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {standards.map((standard) => (
            <button
              key={standard.id}
              onClick={() => setSelectedStandard(standard.id)}
              className={`p-3 rounded-lg border-2 transition-colors ${
                selectedStandard === standard.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-medium">{standard.name}</div>
              <div className="text-sm text-gray-600">{standard.description}</div>
            </button>
          ))}
        </div>
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

export default ComplianceCenter;

