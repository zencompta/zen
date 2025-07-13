import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { Badge } from './ui/badge'
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  AlertTriangle,
  Calendar,
  Download,
  Settings,
  Maximize,
  RefreshCw,
  Eye,
  Layers
} from 'lucide-react'

const AdvancedVisualizations = ({ onBack }) => {
  const [selectedVisualization, setSelectedVisualization] = useState('dashboard')
  const [visualizationData, setVisualizationData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [config, setConfig] = useState({
    theme: 'plotly_white',
    color_palette: 'viridis',
    width: 1200,
    height: 800
  })

  const visualizationTypes = [
    {
      id: 'dashboard',
      name: 'Tableau de Bord Exécutif',
      description: 'Vue d\'ensemble complète avec KPIs et métriques clés',
      icon: BarChart3,
      category: 'executive'
    },
    {
      id: '3d_financial',
      name: 'Analyse Financière 3D',
      description: 'Graphiques 3D pour l\'analyse multi-dimensionnelle',
      icon: Layers,
      category: '3d'
    },
    {
      id: 'risk_heatmap',
      name: 'Carte de Chaleur des Risques',
      description: 'Visualisation des risques par probabilité et impact',
      icon: AlertTriangle,
      category: 'risk'
    },
    {
      id: 'timeline',
      name: 'Chronologie des Événements',
      description: 'Timeline interactive des événements comptables',
      icon: Calendar,
      category: 'timeline'
    },
    {
      id: 'trend_analysis',
      name: 'Analyse de Tendances Animée',
      description: 'Évolution temporelle avec animations',
      icon: TrendingUp,
      category: 'trends'
    },
    {
      id: 'performance_radar',
      name: 'Radar de Performance',
      description: 'Comparaison multi-critères en radar',
      icon: Activity,
      category: 'performance'
    }
  ]

  useEffect(() => {
    loadVisualizationData()
  }, [selectedVisualization])

  const loadVisualizationData = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/visualizations/${selectedVisualization}`)
      const data = await response.json()
      setVisualizationData(data)
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateVisualization = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/generate-visualization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: selectedVisualization,
          config: config,
          data: visualizationData
        })
      })

      const result = await response.json()
      if (result.success) {
        // Afficher la visualisation générée
        const visualizationContainer = document.getElementById('visualization-container')
        if (visualizationContainer) {
          visualizationContainer.innerHTML = result.html
        }
      }
    } catch (error) {
      console.error('Erreur lors de la génération:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const exportVisualization = async (format) => {
    try {
      const response = await fetch('/api/export-visualization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: selectedVisualization,
          format: format,
          config: config
        })
      })

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `visualization_${selectedVisualization}.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Erreur lors de l\'export:', error)
    }
  }

  const selectedVizType = visualizationTypes.find(v => v.id === selectedVisualization)

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={onBack}>
              ← Retour
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Visualisations Avancées</h1>
              <p className="text-gray-600">Créez des visualisations interactives et des tableaux de bord</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => exportVisualization('png')}>
              <Download className="w-4 h-4 mr-2" />
              PNG
            </Button>
            <Button variant="outline" onClick={() => exportVisualization('svg')}>
              <Download className="w-4 h-4 mr-2" />
              SVG
            </Button>
            <Button onClick={generateVisualization} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              {isLoading ? 'Génération...' : 'Générer'}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sélection de visualisation */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Types de Visualisation</CardTitle>
                <CardDescription>
                  Choisissez le type de visualisation à générer
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {visualizationTypes.map((vizType) => {
                    const Icon = vizType.icon
                    return (
                      <div
                        key={vizType.id}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedVisualization === vizType.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedVisualization(vizType.id)}
                      >
                        <div className="flex items-start space-x-3">
                          <Icon className="w-5 h-5 text-blue-600 mt-0.5" />
                          <div className="flex-1">
                            <h4 className="font-medium text-sm">{vizType.name}</h4>
                            <p className="text-xs text-gray-600 mt-1">{vizType.description}</p>
                            <Badge variant="outline" className="text-xs mt-2">
                              {vizType.category}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Configuration */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  Configuration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Thème</label>
                    <Select 
                      value={config.theme} 
                      onValueChange={(value) => setConfig(prev => ({...prev, theme: value}))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="plotly_white">Blanc</SelectItem>
                        <SelectItem value="plotly_dark">Sombre</SelectItem>
                        <SelectItem value="ggplot2">GGPlot2</SelectItem>
                        <SelectItem value="seaborn">Seaborn</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium">Palette de couleurs</label>
                    <Select 
                      value={config.color_palette} 
                      onValueChange={(value) => setConfig(prev => ({...prev, color_palette: value}))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="viridis">Viridis</SelectItem>
                        <SelectItem value="plasma">Plasma</SelectItem>
                        <SelectItem value="blues">Blues</SelectItem>
                        <SelectItem value="reds">Reds</SelectItem>
                        <SelectItem value="greens">Greens</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-sm font-medium">Largeur</label>
                      <Select 
                        value={config.width.toString()} 
                        onValueChange={(value) => setConfig(prev => ({...prev, width: parseInt(value)}))}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="800">800px</SelectItem>
                          <SelectItem value="1200">1200px</SelectItem>
                          <SelectItem value="1600">1600px</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Hauteur</label>
                      <Select 
                        value={config.height.toString()} 
                        onValueChange={(value) => setConfig(prev => ({...prev, height: parseInt(value)}))}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="600">600px</SelectItem>
                          <SelectItem value="800">800px</SelectItem>
                          <SelectItem value="1000">1000px</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Zone de visualisation */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {selectedVizType && <selectedVizType.icon className="w-5 h-5" />}
                    <CardTitle>{selectedVizType?.name}</CardTitle>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Maximize className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <CardDescription>{selectedVizType?.description}</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Zone de visualisation */}
                <div 
                  id="visualization-container"
                  className="w-full bg-white border rounded-lg p-4 min-h-96 flex items-center justify-center"
                  style={{ height: `${config.height}px` }}
                >
                  {isLoading ? (
                    <div className="text-center">
                      <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
                      <p className="text-gray-600">Génération de la visualisation...</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {selectedVizType?.name}
                      </h3>
                      <p className="text-gray-600 mb-4">
                        Cliquez sur "Générer" pour créer la visualisation
                      </p>
                      <Button onClick={generateVisualization}>
                        Générer la visualisation
                      </Button>
                    </div>
                  )}
                </div>

                {/* Informations sur la visualisation */}
                {selectedVisualization && (
                  <div className="mt-6">
                    <Tabs defaultValue="info" className="w-full">
                      <TabsList>
                        <TabsTrigger value="info">Informations</TabsTrigger>
                        <TabsTrigger value="data">Données</TabsTrigger>
                        <TabsTrigger value="options">Options</TabsTrigger>
                      </TabsList>

                      <TabsContent value="info" className="mt-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="p-4 bg-blue-50 rounded-lg">
                            <h4 className="font-medium text-blue-900">Type</h4>
                            <p className="text-blue-800">{selectedVizType?.category}</p>
                          </div>
                          <div className="p-4 bg-green-50 rounded-lg">
                            <h4 className="font-medium text-green-900">Interactivité</h4>
                            <p className="text-green-800">Zoom, Pan, Hover</p>
                          </div>
                          <div className="p-4 bg-purple-50 rounded-lg">
                            <h4 className="font-medium text-purple-900">Export</h4>
                            <p className="text-purple-800">PNG, SVG, HTML</p>
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="data" className="mt-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium mb-2">Sources de données</h4>
                          <ul className="text-sm text-gray-600 space-y-1">
                            <li>• Données financières actuelles</li>
                            <li>• Historique des performances</li>
                            <li>• Benchmarks sectoriels</li>
                            <li>• Évaluations des risques</li>
                          </ul>
                        </div>
                      </TabsContent>

                      <TabsContent value="options" className="mt-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 border rounded-lg">
                            <h4 className="font-medium mb-2">Personnalisation</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              <li>• Couleurs personnalisées</li>
                              <li>• Polices et tailles</li>
                              <li>• Légendes et annotations</li>
                            </ul>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <h4 className="font-medium mb-2">Interactivité</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              <li>• Filtres dynamiques</li>
                              <li>• Drill-down</li>
                              <li>• Tooltips détaillés</li>
                            </ul>
                          </div>
                        </div>
                      </TabsContent>
                    </Tabs>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdvancedVisualizations

