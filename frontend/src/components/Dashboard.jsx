import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import DataImport from './DataImport.jsx'
import ReportGenerator from './ReportGenerator.jsx'
import { 
  FileText, 
  Plus, 
  Calendar, 
  Building, 
  BarChart3, 
  Download,
  Eye,
  ArrowLeft,
  CheckCircle,
  Clock,
  AlertCircle,
  Shield,
  Brain
} from 'lucide-react'

const Dashboard = ({ user, onBack, onAdminAccess, onAnalysisAccess, onAIAccess, onComplianceAccess, onAlertsAccess, onReportsAccess, onVisualizationsAccess, onSubscriptionAccess }) => {
  const [projects, setProjects] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
  const [showDataImport, setShowDataImport] = useState(false)
  const [showReportGenerator, setShowReportGenerator] = useState(false)
  const [currentProjectId, setCurrentProjectId] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [newProject, setNewProject] = useState({
    company_name: '',
    audit_year: new Date().getFullYear(),
    accounting_standard: ''
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:5000/api/audit-projects', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setProjects(data)
      } else {
        setError('Erreur lors du chargement des projets')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
      console.error('Erreur:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    
    if (!newProject.company_name || !newProject.accounting_standard) {
      setError('Veuillez remplir tous les champs obligatoires')
      return
    }

    try {
      const response = await fetch('http://localhost:5000/api/audit-projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(newProject)
      })

      if (response.ok) {
        setSuccess('Projet créé avec succès')
        setShowCreateForm(false)
        setNewProject({
          company_name: '',
          audit_year: new Date().getFullYear(),
          accounting_standard: ''
        })
        loadProjects()
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Erreur lors de la création du projet')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
      console.error('Erreur:', err)
    }
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { label: 'Brouillon', variant: 'secondary', icon: Clock },
      in_progress: { label: 'En cours', variant: 'default', icon: BarChart3 },
      completed: { label: 'Terminé', variant: 'success', icon: CheckCircle }
    }
    
    const config = statusConfig[status] || statusConfig.draft
    const Icon = config.icon
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    )
  }

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('fr-FR')
    } catch {
      return 'Date invalide'
    }
  }

  // Afficher DataImport si demandé
  if (showDataImport) {
    return (
      <DataImport 
        user={user} 
        projectId={currentProjectId} 
        onBack={handleBackToDashboard} 
      />
    )
  }

  // Afficher ReportGenerator si demandé
  if (showReportGenerator) {
    return (
      <ReportGenerator 
        user={user} 
        projectId={currentProjectId} 
        onBack={handleBackToDashboard} 
      />
    )
  }

  const handleImportData = () => {
    setShowDataImport(true)
  }

  const handleGenerateReport = () => {
    setShowReportGenerator(true)
  }

  const handleBackToDashboard = () => {
    setShowDataImport(false)
    setShowReportGenerator(false)
    setCurrentProjectId(null)
    loadProjects() // Recharger les projets
  }

  const handleProjectAction = (projectId, action) => {
    setCurrentProjectId(projectId)
    if (action === 'import') {
      setShowDataImport(true)
    } else if (action === 'report') {
      setShowReportGenerator(true)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Chargement du dashboard...</p>
        </div>
      </div>
    )
  }

  if (selectedProject) {
    return (
      <div className="min-h-screen bg-slate-50">
        {/* Header */}
        <div className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <Button
                  variant="ghost"
                  onClick={() => setSelectedProject(null)}
                  className="flex items-center space-x-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>Retour aux projets</span>
                </Button>
                <div className="h-6 w-px bg-slate-300"></div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">
                    {selectedProject.company_name}
                  </h1>
                  <p className="text-sm text-slate-600">
                    Exercice {selectedProject.audit_year} • {selectedProject.accounting_standard}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-slate-600">Brouillon</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
              <TabsTrigger value="data">Données</TabsTrigger>
              <TabsTrigger value="analysis">Analyse</TabsTrigger>
              <TabsTrigger value="reports">Rapports</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>Informations du Projet</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-sm font-medium text-slate-600">Entreprise</Label>
                          <p className="text-lg font-semibold">{selectedProject.company_name}</p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-slate-600">Exercice</Label>
                          <p className="text-lg font-semibold">{selectedProject.audit_year}</p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-slate-600">Norme</Label>
                          <p className="text-lg font-semibold">{selectedProject.accounting_standard}</p>
                        </div>
                        <div>
                          <Label className="text-sm font-medium text-slate-600">Statut</Label>
                          <div className="mt-1">
                            {getStatusBadge(selectedProject.status)}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="mt-6">
                    <CardHeader>
                      <CardTitle>Progression de l'Audit</CardTitle>
                      <CardDescription>
                        Suivez l'avancement de votre audit étape par étape
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <CheckCircle className="h-4 w-4 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium">Projet créé</p>
                            <p className="text-sm text-slate-600">Configuration initiale terminée</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                            <Clock className="h-4 w-4 text-slate-400" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-slate-600">Import des données</p>
                            <p className="text-sm text-slate-500">En attente</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                            <Clock className="h-4 w-4 text-slate-400" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-slate-600">Analyse des comptes</p>
                            <p className="text-sm text-slate-500">En attente</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                            <Clock className="h-4 w-4 text-slate-400" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-slate-600">Génération du rapport</p>
                            <p className="text-sm text-slate-500">En attente</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div>
                  <Card>
                    <CardHeader>
                      <CardTitle>Actions Rapides</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <Button className="w-full justify-start" variant="outline">
                        <FileText className="h-4 w-4 mr-2" />
                        Importer Balance
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <BarChart3 className="h-4 w-4 mr-2" />
                        Analyser les Comptes
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Download className="h-4 w-4 mr-2" />
                        Exporter Rapport
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="data" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Gestion des Données</CardTitle>
                  <CardDescription>
                    Importez et gérez les données comptables pour l'audit
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <FileText className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                      Fonctionnalité en développement
                    </h3>
                    <p className="text-slate-600 mb-6">
                      L'import et la gestion des données seront bientôt disponibles
                    </p>
                    <Button variant="outline">
                      <Plus className="h-4 w-4 mr-2" />
                      Importer des Données
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analysis" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Analyse des Comptes</CardTitle>
                  <CardDescription>
                    Outils d'analyse et de contrôle des données comptables
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <BarChart3 className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                      Fonctionnalité en développement
                    </h3>
                    <p className="text-slate-600 mb-6">
                      Les outils d'analyse seront bientôt disponibles
                    </p>
                    <Button variant="outline">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Lancer l'Analyse
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="reports" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Rapports d'Audit</CardTitle>
                  <CardDescription>
                    Génération et gestion des rapports d'audit
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <Download className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                      Fonctionnalité en développement
                    </h3>
                    <p className="text-slate-600 mb-6">
                      La génération de rapports sera bientôt disponible
                    </p>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Générer Rapport
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={onBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Retour à l'accueil</span>
              </Button>
              <div className="h-6 w-px bg-slate-300"></div>
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <h1 className="text-2xl font-bold text-slate-900">
                  Dashboard ZenCompta
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-slate-600">
                Bienvenue, {user?.first_name || 'Utilisateur'} {user?.last_name || ''}
              </span>
              {user?.role === 'admin' && onAdminAccess && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onAdminAccess}
                  className="text-blue-600 border-blue-600 hover:bg-blue-50"
                >
                  <Shield className="h-4 w-4 mr-2" />
                  Administration
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alerts */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {success}
            </AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Projets</p>
                  <p className="text-3xl font-bold text-slate-900">{projects.length}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">En Cours</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {projects.filter(p => p.status === 'in_progress').length}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Terminés</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {projects.filter(p => p.status === 'completed').length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Cette Année</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {projects.filter(p => p.audit_year === new Date().getFullYear()).length}
                  </p>
                </div>
                <Calendar className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Projects List */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-slate-900">Mes Projets d'Audit</h2>
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nouveau Projet
              </Button>
            </div>

            {projects.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <FileText className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    Aucun projet d'audit
                  </h3>
                  <p className="text-slate-600 mb-6">
                    Commencez par créer votre premier projet d'audit pour organiser votre travail.
                  </p>
                  <Button onClick={() => setShowCreateForm(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Créer votre premier projet
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {projects.map((project) => (
                  <Card 
                    key={project.id} 
                    className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setSelectedProject(project)}
                  >
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-lg font-semibold text-slate-900">
                              {project.company_name}
                            </h3>
                            {getStatusBadge(project.status)}
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
                            <div className="flex items-center space-x-2">
                              <Calendar className="h-4 w-4" />
                              <span>Exercice {project.audit_year}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Building className="h-4 w-4" />
                              <span>{project.accounting_standard}</span>
                            </div>
                          </div>
                          <p className="text-sm text-slate-500 mt-2">
                            Créé le {formatDate(project.created_at)}
                          </p>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Advanced Features */}
            <Card>
              <CardHeader>
                <CardTitle>Fonctionnalités Avancées</CardTitle>
                <CardDescription>
                  Exploitez la puissance de l'IA et de l'analyse avancée
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onAnalysisAccess}
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analyse Avancée
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onAIAccess}
                >
                  <Brain className="h-4 w-4 mr-2" />
                  Intelligence Artificielle
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onComplianceAccess}
                >
                  <Shield className="h-4 w-4 mr-2" />
                  Conformité Réglementaire
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onAlertsAccess}
                >
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Tableau de Bord Alertes
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onReportsAccess}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Générateur de Rapports
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onVisualizationsAccess}
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Visualisations Avancées
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={onSubscriptionAccess}
                >
                  <Shield className="h-4 w-4 mr-2" />
                  Gestion Abonnement
                </Button>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions Rapides</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => setShowCreateForm(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nouveau Projet
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={handleImportData}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Importer des Données
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={handleGenerateReport}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Rapport Global
                </Button>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Activité Récente</CardTitle>
              </CardHeader>
              <CardContent>
                {projects.length > 0 ? (
                  <div className="space-y-3">
                    {projects.slice(0, 3).map((project) => (
                      <div key={project.id} className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">
                            {project.company_name}
                          </p>
                          <p className="text-xs text-slate-500">
                            Modifié le {formatDate(project.updated_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-600">Aucune activité récente</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Create Project Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Nouveau Projet d'Audit</CardTitle>
              <CardDescription>
                Créez un nouveau projet pour organiser votre audit comptable
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <Label htmlFor="company_name">Nom de l'entreprise</Label>
                  <Input
                    id="company_name"
                    placeholder="Ex: SARL Exemple"
                    value={newProject.company_name}
                    onChange={(e) => setNewProject({
                      ...newProject,
                      company_name: e.target.value
                    })}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="audit_year">Exercice d'audit</Label>
                  <Input
                    id="audit_year"
                    type="number"
                    min="2020"
                    max="2030"
                    value={newProject.audit_year}
                    onChange={(e) => setNewProject({
                      ...newProject,
                      audit_year: parseInt(e.target.value)
                    })}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="accounting_standard">Norme comptable</Label>
                  <Select
                    value={newProject.accounting_standard}
                    onValueChange={(value) => setNewProject({
                      ...newProject,
                      accounting_standard: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choisir une norme" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IFRS">Normes IFRS</SelectItem>
                      <SelectItem value="SYSCOHADA">SYSCOHADA</SelectItem>
                      <SelectItem value="US_GAAP">US GAAP</SelectItem>
                      <SelectItem value="PCG">Plan Comptable Général</SelectItem>
                      <SelectItem value="OTHER">Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex space-x-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowCreateForm(false)}
                  >
                    Annuler
                  </Button>
                  <Button type="submit" className="flex-1">
                    Créer le Projet
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default Dashboard

