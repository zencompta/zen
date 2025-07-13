import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  FileText,
  Shield,
  Zap,
  Eye,
  Filter,
  Calendar,
  BarChart3,
  PieChart,
  RefreshCw
} from 'lucide-react';

const AlertsDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);

  const periods = [
    { id: '24h', name: '24 heures' },
    { id: '7d', name: '7 jours' },
    { id: '30d', name: '30 jours' },
    { id: '90d', name: '90 jours' }
  ];

  const filters = [
    { id: 'all', name: 'Toutes les alertes' },
    { id: 'critical', name: 'Critiques' },
    { id: 'high', name: 'Importantes' },
    { id: 'compliance', name: 'Conformité' },
    { id: 'anomaly', name: 'Anomalies' },
    { id: 'deadline', name: 'Échéances' }
  ];

  useEffect(() => {
    loadAlerts();
    loadStatistics();
  }, [selectedPeriod, selectedFilter]);

  const loadAlerts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/alerts/dashboard?period=${selectedPeriod}&filter=${selectedFilter}`);
      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (error) {
      console.error('Erreur chargement alertes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch(`/api/alerts/statistics?period=${selectedPeriod}`);
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Erreur chargement statistiques:', error);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'high':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'text-red-600 bg-red-100';
      case 'acknowledged':
        return 'text-yellow-600 bg-yellow-100';
      case 'resolved':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const renderStatisticsCards = () => {
    if (!statistics) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total des alertes */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Bell className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">
                {statistics.total_alerts || 0}
              </div>
              <div className="text-sm text-gray-600">Total alertes</div>
            </div>
          </div>
          <div className="mt-4 flex items-center">
            {statistics.alerts_trend > 0 ? (
              <TrendingUp className="h-4 w-4 text-red-500 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 text-green-500 mr-1" />
            )}
            <span className={`text-sm ${statistics.alerts_trend > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {Math.abs(statistics.alerts_trend)}% vs période précédente
            </span>
          </div>
        </div>

        {/* Alertes critiques */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">
                {statistics.by_priority?.critical || 0}
              </div>
              <div className="text-sm text-gray-600">Critiques</div>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-xs text-gray-500">
              {statistics.by_priority?.high || 0} importantes, {statistics.by_priority?.medium || 0} moyennes
            </div>
          </div>
        </div>

        {/* Temps de résolution moyen */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Clock className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">
                {statistics.resolution_time?.average_hours?.toFixed(1) || 0}h
              </div>
              <div className="text-sm text-gray-600">Temps résolution</div>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-xs text-gray-500">
              Médiane: {statistics.resolution_time?.median_hours?.toFixed(1) || 0}h
            </div>
          </div>
        </div>

        {/* Score de conformité */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Shield className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">
                {statistics.compliance_score ? (statistics.compliance_score * 100).toFixed(0) : 0}%
              </div>
              <div className="text-sm text-gray-600">Conformité</div>
            </div>
          </div>
          <div className="mt-4">
            <div className={`text-xs ${
              (statistics.compliance_score || 0) >= 0.9 ? 'text-green-600' :
              (statistics.compliance_score || 0) >= 0.7 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {(statistics.compliance_score || 0) >= 0.9 ? 'Excellent' :
               (statistics.compliance_score || 0) >= 0.7 ? 'Bon' : 'À améliorer'}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderTrendsChart = () => {
    if (!statistics?.trends) return null;

    return (
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Tendances des alertes</h3>
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-600">Derniers {selectedPeriod}</span>
          </div>
        </div>
        
        {/* Graphique simplifié */}
        <div className="space-y-4">
          {Object.entries(statistics.trends.daily_counts || {}).slice(-7).map(([date, count]) => (
            <div key={date} className="flex items-center">
              <div className="w-20 text-sm text-gray-600">{new Date(date).toLocaleDateString()}</div>
              <div className="flex-1 mx-4">
                <div className="bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${Math.min(100, (count / Math.max(...Object.values(statistics.trends.daily_counts))) * 100)}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-8 text-sm text-gray-900 text-right">{count}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderDistributionChart = () => {
    if (!statistics?.by_type) return null;

    return (
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Répartition par type</h3>
          <PieChart className="h-4 w-4 text-gray-400" />
        </div>
        
        <div className="space-y-3">
          {Object.entries(statistics.by_type).map(([type, count]) => {
            const total = Object.values(statistics.by_type).reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;
            
            return (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    type === 'compliance_violation' ? 'bg-red-500' :
                    type === 'pattern_anomaly' ? 'bg-yellow-500' :
                    type === 'deadline_approaching' ? 'bg-blue-500' :
                    'bg-gray-500'
                  }`}></div>
                  <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 mr-2">{percentage}%</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Tableau de Bord des Alertes
        </h1>
        <p className="text-gray-600">
          Surveillez et gérez toutes vos alertes de conformité et d'anomalies
        </p>
      </div>

      {/* Contrôles de filtrage */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                {periods.map((period) => (
                  <option key={period.id} value={period.id}>
                    {period.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                {filters.map((filter) => (
                  <option key={filter.id} value={filter.id}>
                    {filter.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <button
            onClick={() => { loadAlerts(); loadStatistics(); }}
            disabled={isLoading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
        </div>
      </div>

      {/* Cartes de statistiques */}
      {renderStatisticsCards()}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Graphique des tendances */}
        {renderTrendsChart()}
        
        {/* Graphique de répartition */}
        {renderDistributionChart()}
      </div>

      {/* Liste des alertes */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Alertes récentes</h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {alerts.map((alert, index) => (
            <div key={index} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg ${
                    alert.alert_type === 'compliance_violation' ? 'bg-red-100' :
                    alert.alert_type === 'pattern_anomaly' ? 'bg-yellow-100' :
                    alert.alert_type === 'deadline_approaching' ? 'bg-blue-100' :
                    'bg-gray-100'
                  }`}>
                    {alert.alert_type === 'compliance_violation' ? (
                      <Shield className="h-5 w-5 text-red-600" />
                    ) : alert.alert_type === 'pattern_anomaly' ? (
                      <Zap className="h-5 w-5 text-yellow-600" />
                    ) : alert.alert_type === 'deadline_approaching' ? (
                      <Clock className="h-5 w-5 text-blue-600" />
                    ) : (
                      <Bell className="h-5 w-5 text-gray-600" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">{alert.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(alert.priority)}`}>
                        {alert.priority}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(alert.status)}`}>
                        {alert.status}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{alert.description}</p>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>{new Date(alert.created_at).toLocaleString()}</span>
                      {alert.compliance_standard && (
                        <span>Norme: {alert.compliance_standard.toUpperCase()}</span>
                      )}
                      {alert.affected_entities?.length > 0 && (
                        <span>{alert.affected_entities.length} entité(s) affectée(s)</span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <CheckCircle className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              {alert.remediation_actions?.length > 0 && (
                <div className="mt-4 pl-12">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <div className="text-sm font-medium text-blue-800 mb-1">
                      Actions recommandées:
                    </div>
                    <ul className="text-sm text-blue-700 space-y-1">
                      {alert.remediation_actions.slice(0, 2).map((action, i) => (
                        <li key={i} className="flex items-start">
                          <span className="mr-2">•</span>
                          {action}
                        </li>
                      ))}
                      {alert.remediation_actions.length > 2 && (
                        <li className="text-blue-600">
                          +{alert.remediation_actions.length - 2} autres actions...
                        </li>
                      )}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {alerts.length === 0 && !isLoading && (
            <div className="p-12 text-center">
              <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune alerte</h3>
              <p className="text-gray-600">
                {selectedFilter === 'all' 
                  ? 'Aucune alerte pour la période sélectionnée'
                  : `Aucune alerte ${filters.find(f => f.id === selectedFilter)?.name.toLowerCase()} pour la période sélectionnée`
                }
              </p>
            </div>
          )}
          
          {isLoading && (
            <div className="p-12 text-center">
              <RefreshCw className="h-8 w-8 text-blue-600 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600">Chargement des alertes...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertsDashboard;

