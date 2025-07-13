import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
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
  Shield
} from 'lucide-react'

const Dashboard = ({ user, onBack, onAdminAccess }) => {
  const [projects, setProjects] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
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
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:5000/api/audit-projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(newProject)
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess('Projet créé avec succès !')
        setProjects([...projects, data])
        setNewProject({
          company_name: '',
          audit_year: new Date().getFullYear(),
          accounting_standard: ''
        })
        setShowCreateForm(false)
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(data.error || 'Erreur lors de la création du projet')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteProject = async (projectId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce projet ?')) {
      return
    }

    try {
      const response = await fetch(`http://localhost:5000/api/audit-projects/${projectId}`, {
        method: 'DELETE',
        credentials: 'include'
      })

      if (response.ok) {
        setProjects(projects.filter(p => p.id !== projectId))
        setSuccess('Projet supprimé avec succès')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Erreur lors de la suppression')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
    }
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { label: 'Brouillon', variant: 'secondary', icon: Edit },
      in_progress: { label: 'En cours', variant: 'default', icon: Clock },
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

  const getStandardLabel = (standard) => {
    const standards = {
      'IFRS': 'Normes IFRS',
      'SYSCOHADA': 'SYSCOHADA',
      'US_GAAP': 'US GAAP',
      'PCG': 'Plan Comptable Général',
      'OTHER': 'Autre'
    }
    return standards[standard] || standard
  }

  if (selectedProject) {
    return (
      <ProjectDetail 
        project={selectedProject} 
        onBack={() => setSelectedProject(null)}
        user={user}
      />
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
              <h1 className="text-2xl font-bold text-slate-900">
                Dashboard ZenCompta
              </h1>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-slate-600">
                Bienvenue, {user.first_name} {user.last_name}
              </span>
              {user.role === 'admin' && (
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
                  <p className="text-sm font-medium text-slate-600">En cours</p>
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
                  <p className="text-sm font-medium text-slate-600">Cette année</p>
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
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Mes Projets d'Audit</CardTitle>
                    <CardDescription>
                      Gérez vos projets d'audit comptable
                    </CardDescription>
                  </div>
                  <Button
                    onClick={() => setShowCreateForm(true)}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Nouveau Projet
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-slate-600">Chargement...</p>
                  </div>
                ) : projects.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <p className="text-slate-600 mb-4">Aucun projet d'audit pour le moment</p>
                    <Button
                      onClick={() => setShowCreateForm(true)}
                      variant="outline"
                    >
                      Créer votre premier projet
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {projects.map((project) => (
                      <div
                        key={project.id}
                        className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                        onClick={() => setSelectedProject(project)}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-semibold text-slate-900 mb-1">
                              {project.company_name}
                            </h3>
                            <p className="text-sm text-slate-600">
                              Exercice {project.audit_year} • {getStandardLabel(project.accounting_standard)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {getStatusBadge(project.status)}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDeleteProject(project.id)
                              }}
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        <div className="flex justify-between items-center text-sm text-slate-500">
                          <span>
                            Créé le {new Date(project.created_at).toLocaleDateString('fr-FR')}
                          </span>
                          <div className="flex items-center space-x-2">
                            <Eye className="h-4 w-4" />
                            <span>Voir le projet</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions Rapides</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => setShowCreateForm(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nouveau Projet
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  disabled
                >
                  <Download className="h-4 w-4 mr-2" />
                  Importer des Données
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  disabled
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
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
                {projects.length === 0 ? (
                  <p className="text-sm text-slate-600">Aucune activité récente</p>
                ) : (
                  <div className="space-y-3">
                    {projects.slice(0, 3).map((project) => (
                      <div key={project.id} className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">
                            {project.company_name}
                          </p>
                          <p className="text-xs text-slate-500">
                            Modifié le {new Date(project.updated_at).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Create Project Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-4">
                Nouveau Projet d'Audit
              </h2>
              
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <Label htmlFor="company_name">Nom de l'entreprise</Label>
                  <Input
                    id="company_name"
                    value={newProject.company_name}
                    onChange={(e) => setNewProject({
                      ...newProject,
                      company_name: e.target.value
                    })}
                    placeholder="Ex: SARL Exemple"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="audit_year">Exercice d'audit</Label>
                  <Input
                    id="audit_year"
                    type="number"
                    value={newProject.audit_year}
                    onChange={(e) => setNewProject({
                      ...newProject,
                      audit_year: parseInt(e.target.value)
                    })}
                    min="2020"
                    max="2030"
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

                <div className="flex justify-end space-x-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowCreateForm(false)}
                  >
                    Annuler
                  </Button>
                  <Button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Création...' : 'Créer le Projet'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Composant pour les détails d'un projet
const ProjectDetail = ({ project, onBack, user }) => {
  const [activeTab, setActiveTab] = useState('overview')

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
                <span>Retour aux projets</span>
              </Button>
              <div className="h-6 w-px bg-slate-300"></div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">
                  {project.company_name}
                </h1>
                <p className="text-sm text-slate-600">
                  Exercice {project.audit_year} • {project.accounting_standard}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Badge variant="outline">
                {project.status === 'draft' && 'Brouillon'}
                {project.status === 'in_progress' && 'En cours'}
                {project.status === 'completed' && 'Terminé'}
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
            <TabsTrigger value="data">Données</TabsTrigger>
            <TabsTrigger value="analysis">Analyse</TabsTrigger>
            <TabsTrigger value="reports">Rapports</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Informations du Projet</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium text-slate-600">Entreprise</Label>
                        <p className="text-slate-900">{project.company_name}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-slate-600">Exercice</Label>
                        <p className="text-slate-900">{project.audit_year}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-slate-600">Norme</Label>
                        <p className="text-slate-900">{project.accounting_standard}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-slate-600">Statut</Label>
                        <p className="text-slate-900 capitalize">{project.status}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Progression de l'Audit</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Collecte des données</span>
                        <Badge variant="secondary">À faire</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Analyse des comptes</span>
                        <Badge variant="secondary">À faire</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Contrôles substantifs</span>
                        <Badge variant="secondary">À faire</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Rapport d'audit</span>
                        <Badge variant="secondary">À faire</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button className="w-full justify-start" disabled>
                      <FileText className="h-4 w-4 mr-2" />
                      Importer Balance
                    </Button>
                    <Button className="w-full justify-start" disabled>
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Analyser les Comptes
                    </Button>
                    <Button className="w-full justify-start" disabled>
                      <Download className="h-4 w-4 mr-2" />
                      Générer Rapport
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Historique</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        <span className="text-slate-600">
                          Projet créé le {new Date(project.created_at).toLocaleDateString('fr-FR')}
                        </span>
                      </div>
                    </div>
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
                  <h3 className="text-lg font-medium text-slate-900 mb-2">
                    Fonctionnalité en développement
                  </h3>
                  <p className="text-slate-600 mb-4">
                    L'import et la gestion des données seront bientôt disponibles
                  </p>
                  <Button disabled>
                    Importer des Données
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analysis" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Analyse et Contrôles</CardTitle>
                <CardDescription>
                  Effectuez les contrôles d'audit et analyses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <BarChart3 className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 mb-2">
                    Outils d'analyse en développement
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Les outils d'analyse automatisée seront bientôt disponibles
                  </p>
                  <Button disabled>
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
                  Générez et téléchargez vos rapports d'audit
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Download className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 mb-2">
                    Génération de rapports en développement
                  </h3>
                  <p className="text-slate-600 mb-4">
                    La génération automatique de rapports sera bientôt disponible
                  </p>
                  <Button disabled>
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

export default Dashboard

