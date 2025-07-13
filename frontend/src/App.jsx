import { useState, useEffect } from 'react'
import './App.css'
import AuthModal from './components/AuthModal'
import Dashboard from './components/Dashboard'
import AdminDashboard from './components/AdminDashboard'
import AdvancedAnalysis from './components/AdvancedAnalysis'
import AIFeatures from './components/AIFeatures'
import ComplianceCenter from './components/ComplianceCenter'
import AlertsDashboard from './components/AlertsDashboard'
import ReportGenerator from './components/ReportGenerator'
import AdvancedVisualizations from './components/AdvancedVisualizations'
import SubscriptionManager from './components/SubscriptionManager'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Badge } from './components/ui/badge'
import { Input } from './components/ui/input'
import { Textarea } from './components/ui/textarea'
import { 
  CheckCircle, 
  Shield, 
  BarChart3, 
  FileText, 
  Users, 
  Award,
  ArrowRight,
  Star,
  Mail,
  Phone,
  MapPin,
  Download,
  Play,
  Menu,
  X,
  User,
  LogOut
} from 'lucide-react'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentView, setCurrentView] = useState('home') // home, dashboard, admin, analysis, ai, compliance, alerts, reports, visualizations
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: ''
  })

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/status')
      const data = await response.json()
      if (data.authenticated) {
        setUser(data.user)
      }
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'authentification:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAuthSuccess = (userData) => {
    setUser(userData)
    setIsAuthModalOpen(false)
    // Rediriger vers le dashboard après connexion
    setCurrentView('dashboard')
  }

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
      setUser(null)
      setCurrentView('home')
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    }
  }

  const handleFormChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleContactSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        alert('Message envoyé avec succès!')
        setFormData({ name: '', email: '', company: '', message: '' })
      }
    } catch (error) {
      console.error('Erreur lors de l\'envoi:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement de ZenCompta...</p>
        </div>
      </div>
    )
  }

  // Rendu conditionnel basé sur la vue actuelle
  if (currentView === 'dashboard') {
    return (
      <Dashboard 
        user={user} 
        onBack={() => setCurrentView('home')}
        onAdminAccess={() => setCurrentView('admin')}
        onAnalysisAccess={() => setCurrentView('analysis')}
        onAIAccess={() => setCurrentView('ai')}
        onComplianceAccess={() => setCurrentView('compliance')}
        onAlertsAccess={() => setCurrentView('alerts')}
        onReportsAccess={() => setCurrentView('reports')}
        onVisualizationsAccess={() => setCurrentView('visualizations')}
        onSubscriptionAccess={() => setCurrentView('subscription')}
      />
    )
  }

  if (currentView === 'admin') {
    return <AdminDashboard onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'analysis') {
    return <AdvancedAnalysis onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'ai') {
    return <AIFeatures onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'compliance') {
    return <ComplianceCenter onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'alerts') {
    return <AlertsDashboard onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'reports') {
    return <ReportGenerator onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'visualizations') {
    return <AdvancedVisualizations onBack={() => setCurrentView('dashboard')} />
  }

  if (currentView === 'subscription') {
    return <SubscriptionManager user={user} onBack={() => setCurrentView('dashboard')} />
  }

  // Page d'accueil
  const renderHomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <Shield className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">ZenCompta</span>
              </div>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition-colors">Fonctionnalités</a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition-colors">Tarifs</a>
              <a href="#contact" className="text-gray-700 hover:text-blue-600 transition-colors">Contact</a>
              
              {user ? (
                <div className="flex items-center space-x-4">
                  <span className="text-gray-700">Bonjour, {user.first_name}</span>
                  <Button 
                    variant="outline" 
                    onClick={() => setCurrentView('dashboard')}
                  >
                    <User className="w-4 h-4 mr-2" />
                    Dashboard
                  </Button>
                  <Button variant="outline" onClick={handleLogout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Déconnexion
                  </Button>
                </div>
              ) : (
                <Button onClick={() => setIsAuthModalOpen(true)}>
                  Se connecter
                </Button>
              )}
            </div>

            <div className="md:hidden flex items-center">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-700 hover:text-blue-600"
              >
                {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Menu mobile */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#features" className="block px-3 py-2 text-gray-700">Fonctionnalités</a>
              <a href="#pricing" className="block px-3 py-2 text-gray-700">Tarifs</a>
              <a href="#contact" className="block px-3 py-2 text-gray-700">Contact</a>
              {!user && (
                <Button 
                  className="w-full mt-2" 
                  onClick={() => setIsAuthModalOpen(true)}
                >
                  Se connecter
                </Button>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            L'audit comptable
            <span className="text-blue-600"> révolutionné</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            ZenCompta transforme vos processus d'audit avec l'intelligence artificielle, 
            des visualisations avancées et des rapports professionnels automatisés.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {user ? (
              <Button 
                size="lg" 
                className="text-lg px-8 py-3"
                onClick={() => setCurrentView('dashboard')}
              >
                Accéder au Dashboard
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            ) : (
              <Button 
                size="lg" 
                className="text-lg px-8 py-3"
                onClick={() => setIsAuthModalOpen(true)}
              >
                Commencer gratuitement
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            )}
            <Button variant="outline" size="lg" className="text-lg px-8 py-3">
              <Play className="mr-2 h-5 w-5" />
              Voir la démo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Fonctionnalités Avancées
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Une suite complète d'outils pour moderniser vos audits comptables
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Analyse Avancée */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <BarChart3 className="h-12 w-12 text-blue-600 mb-4" />
                <CardTitle>Analyse Comptable Avancée</CardTitle>
                <CardDescription>
                  Détection automatique, OCR, validation croisée et analyse de cohérence temporelle
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Détection automatique du type de fichier</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />OCR pour documents scannés</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Validation croisée entre documents</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Détection d'écritures suspectes</li>
                </ul>
              </CardContent>
            </Card>

            {/* Intelligence Artificielle */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <Shield className="h-12 w-12 text-purple-600 mb-4" />
                <CardTitle>Intelligence Artificielle</CardTitle>
                <CardDescription>
                  Modèles ML pour classification, prédiction d'anomalies et suggestions automatiques
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Classification automatique</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Prédiction d'anomalies</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Suggestions de corrections</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Apprentissage adaptatif</li>
                </ul>
              </CardContent>
            </Card>

            {/* Conformité Réglementaire */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <Award className="h-12 w-12 text-green-600 mb-4" />
                <CardTitle>Conformité Réglementaire</CardTitle>
                <CardDescription>
                  Moteur de règles multi-normes avec validation en temps réel
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Support IFRS, SYSCOHADA, SYSCEBNL</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Check-lists automatiques</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Validation temps réel</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Alertes de non-conformité</li>
                </ul>
              </CardContent>
            </Card>

            {/* Templates Professionnels */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <FileText className="h-12 w-12 text-orange-600 mb-4" />
                <CardTitle>Templates Professionnels</CardTitle>
                <CardDescription>
                  Rapports personnalisables avec branding client et formats multiples
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Templates par secteur</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Branding personnalisé</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />PDF, Word, Excel, PowerPoint</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Rapports interactifs</li>
                </ul>
              </CardContent>
            </Card>

            {/* Visualisations Avancées */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <BarChart3 className="h-12 w-12 text-red-600 mb-4" />
                <CardTitle>Visualisations Avancées</CardTitle>
                <CardDescription>
                  Graphiques 3D, tableaux de bord exécutifs et cartes de chaleur
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Graphiques 3D et animations</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Tableaux de bord exécutifs</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Cartes de chaleur des risques</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Chronologies visuelles</li>
                </ul>
              </CardContent>
            </Card>

            {/* Contenu Intelligent */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <Users className="h-12 w-12 text-indigo-600 mb-4" />
                <CardTitle>Contenu Intelligent</CardTitle>
                <CardDescription>
                  Génération automatique de commentaires et recommandations contextuelles
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Commentaires automatiques</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Recommandations contextuelles</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Comparaisons sectorielles</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-green-500 mr-2" />Benchmarking automatique</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Contactez-nous
            </h2>
            <p className="text-xl text-gray-600">
              Prêt à révolutionner vos audits comptables ?
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Parlons de votre projet</h3>
              <form onSubmit={handleContactSubmit} className="space-y-6">
                <div>
                  <Input
                    placeholder="Votre nom"
                    value={formData.name}
                    onChange={(e) => handleFormChange('name', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Input
                    type="email"
                    placeholder="Votre email"
                    value={formData.email}
                    onChange={(e) => handleFormChange('email', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Input
                    placeholder="Votre entreprise"
                    value={formData.company}
                    onChange={(e) => handleFormChange('company', e.target.value)}
                  />
                </div>
                <div>
                  <Textarea
                    placeholder="Votre message"
                    value={formData.message}
                    onChange={(e) => handleFormChange('message', e.target.value)}
                    rows={4}
                    required
                  />
                </div>
                <Button type="submit" size="lg" className="w-full">
                  Envoyer le message
                </Button>
              </form>
            </div>

            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Informations de contact</h3>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <Mail className="h-6 w-6 text-blue-600 mr-3" />
                    <span>contact@zencompta.com</span>
                  </div>
                  <div className="flex items-center">
                    <Phone className="h-6 w-6 text-blue-600 mr-3" />
                    <span>+33 1 23 45 67 89</span>
                  </div>
                  <div className="flex items-center">
                    <MapPin className="h-6 w-6 text-blue-600 mr-3" />
                    <span>Paris, France</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Pourquoi choisir ZenCompta ?</h4>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center">
                    <Star className="h-5 w-5 text-yellow-500 mr-2" />
                    Solution complète et intégrée
                  </li>
                  <li className="flex items-center">
                    <Star className="h-5 w-5 text-yellow-500 mr-2" />
                    Intelligence artificielle avancée
                  </li>
                  <li className="flex items-center">
                    <Star className="h-5 w-5 text-yellow-500 mr-2" />
                    Support multi-normes comptables
                  </li>
                  <li className="flex items-center">
                    <Star className="h-5 w-5 text-yellow-500 mr-2" />
                    Interface moderne et intuitive
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <Shield className="h-8 w-8 text-blue-400" />
                <span className="ml-2 text-xl font-bold">ZenCompta</span>
              </div>
              <p className="text-gray-400">
                La plateforme d'audit comptable nouvelle génération
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Produit</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Fonctionnalités</li>
                <li>Tarifs</li>
                <li>Documentation</li>
                <li>API</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Entreprise</h4>
              <ul className="space-y-2 text-gray-400">
                <li>À propos</li>
                <li>Blog</li>
                <li>Carrières</li>
                <li>Contact</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Centre d'aide</li>
                <li>Communauté</li>
                <li>Statut</li>
                <li>Sécurité</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 ZenCompta. Tous droits réservés.</p>
          </div>
        </div>
      </footer>

      {/* Modal d'authentification */}
      <AuthModal 
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  )

  return renderHomePage()
}

export default App

