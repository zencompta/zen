import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Textarea } from './ui/textarea'
import { Badge } from './ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { 
  FileText, 
  Download, 
  Settings, 
  Palette, 
  Building2,
  Upload,
  Eye,
  Save,
  Trash2,
  Copy,
  Star
} from 'lucide-react'

const ReportGenerator = ({ onBack }) => {
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [templates, setTemplates] = useState([])
  const [sectors, setSectors] = useState({})
  const [selectedSector, setSelectedSector] = useState('all')
  const [brandingConfig, setBrandingConfig] = useState({
    company_name: '',
    company_address: '',
    company_phone: '',
    company_email: '',
    primary_color: '#1f2937',
    secondary_color: '#3b82f6',
    accent_color: '#10b981',
    font_family: 'Arial',
    header_text: '',
    footer_text: '',
    logo_path: null
  })
  const [reportData, setReportData] = useState({})
  const [outputFormat, setOutputFormat] = useState('PDF')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedReports, setGeneratedReports] = useState([])

  useEffect(() => {
    loadTemplates()
    loadSectors()
    loadGeneratedReports()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/report-templates')
      const data = await response.json()
      setTemplates(data.templates || [])
    } catch (error) {
      console.error('Erreur lors du chargement des templates:', error)
    }
  }

  const loadSectors = async () => {
    try {
      const response = await fetch('/api/report-templates/sectors')
      const data = await response.json()
      setSectors(data.sectors || {})
    } catch (error) {
      console.error('Erreur lors du chargement des secteurs:', error)
    }
  }

  const loadGeneratedReports = async () => {
    try {
      const response = await fetch('/api/generated-reports')
      const data = await response.json()
      setGeneratedReports(data.reports || [])
    } catch (error) {
      console.error('Erreur lors du chargement des rapports générés:', error)
    }
  }

  const filteredTemplates = selectedSector === 'all' 
    ? templates 
    : templates.filter(t => t.sector === selectedSector)

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template)
    // Initialiser les données du rapport avec les sections du template
    const initialData = {}
    template.sections.forEach(section => {
      initialData[section.type] = ''
    })
    setReportData(initialData)
  }

  const handleBrandingChange = (field, value) => {
    setBrandingConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleReportDataChange = (sectionType, value) => {
    setReportData(prev => ({
      ...prev,
      [sectionType]: value
    }))
  }

  const handleLogoUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setBrandingConfig(prev => ({
          ...prev,
          logo_path: e.target.result
        }))
      }
      reader.readAsDataURL(file)
    }
  }

  const generateReport = async () => {
    if (!selectedTemplate) {
      alert('Veuillez sélectionner un template')
      return
    }

    setIsGenerating(true)
    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          template_id: selectedTemplate.template_id,
          data: reportData,
          branding: brandingConfig,
          output_format: outputFormat
        })
      })

      const result = await response.json()
      if (result.success) {
        alert('Rapport généré avec succès!')
        loadGeneratedReports()
        // Télécharger automatiquement le rapport
        window.open(result.download_url, '_blank')
      } else {
        alert('Erreur lors de la génération: ' + result.error)
      }
    } catch (error) {
      console.error('Erreur lors de la génération:', error)
      alert('Erreur lors de la génération du rapport')
    } finally {
      setIsGenerating(false)
    }
  }

  const saveTemplate = async () => {
    try {
      const customTemplate = {
        name: `Template personnalisé - ${new Date().toLocaleDateString()}`,
        description: 'Template créé par l\'utilisateur',
        sector: selectedSector,
        template_type: 'custom',
        sections: selectedTemplate?.sections || [],
        branding: brandingConfig
      }

      const response = await fetch('/api/report-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(customTemplate)
      })

      const result = await response.json()
      if (result.success) {
        alert('Template sauvegardé avec succès!')
        loadTemplates()
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
    }
  }

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
              <h1 className="text-3xl font-bold text-gray-900">Générateur de Rapports</h1>
              <p className="text-gray-600">Créez des rapports professionnels avec templates personnalisables</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={saveTemplate}>
              <Save className="w-4 h-4 mr-2" />
              Sauvegarder Template
            </Button>
            <Button onClick={generateReport} disabled={!selectedTemplate || isGenerating}>
              <FileText className="w-4 h-4 mr-2" />
              {isGenerating ? 'Génération...' : 'Générer Rapport'}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sélection de template */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Templates Disponibles
                </CardTitle>
                <CardDescription>
                  Choisissez un template adapté à votre secteur d'activité
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Filtre par secteur */}
                <div className="mb-4">
                  <Label htmlFor="sector-select">Secteur d'activité</Label>
                  <Select value={selectedSector} onValueChange={setSelectedSector}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner un secteur" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tous les secteurs</SelectItem>
                      {Object.entries(sectors).map(([key, value]) => (
                        <SelectItem key={key} value={key}>{value}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Liste des templates */}
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {filteredTemplates.map((template) => (
                    <div
                      key={template.template_id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedTemplate?.template_id === template.template_id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleTemplateSelect(template)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{template.name}</h4>
                          <p className="text-xs text-gray-600 mt-1">{template.description}</p>
                          <div className="flex items-center mt-2 space-x-2">
                            <Badge variant="secondary" className="text-xs">
                              {template.template_type}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {template.sector}
                            </Badge>
                          </div>
                        </div>
                        {template.template_type === 'custom' && (
                          <Star className="w-4 h-4 text-yellow-500" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Rapports générés */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Download className="w-5 h-5 mr-2" />
                  Rapports Générés
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {generatedReports.map((report, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border rounded">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{report.name}</p>
                        <p className="text-xs text-gray-600">{report.date}</p>
                      </div>
                      <div className="flex space-x-1">
                        <Button size="sm" variant="outline" onClick={() => window.open(report.url, '_blank')}>
                          <Eye className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => window.open(report.download_url, '_blank')}>
                          <Download className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Configuration et contenu */}
          <div className="lg:col-span-2">
            {selectedTemplate ? (
              <Tabs defaultValue="content" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="content">Contenu</TabsTrigger>
                  <TabsTrigger value="branding">Branding</TabsTrigger>
                  <TabsTrigger value="settings">Paramètres</TabsTrigger>
                </TabsList>

                {/* Onglet Contenu */}
                <TabsContent value="content">
                  <Card>
                    <CardHeader>
                      <CardTitle>Contenu du Rapport</CardTitle>
                      <CardDescription>
                        Remplissez les sections du template sélectionné
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {selectedTemplate.sections.map((section) => (
                          <div key={section.type}>
                            <Label htmlFor={section.type} className="flex items-center">
                              {section.title}
                              {section.required && <span className="text-red-500 ml-1">*</span>}
                            </Label>
                            <Textarea
                              id={section.type}
                              placeholder={`Contenu pour ${section.title.toLowerCase()}...`}
                              value={reportData[section.type] || ''}
                              onChange={(e) => handleReportDataChange(section.type, e.target.value)}
                              className="mt-2"
                              rows={4}
                            />
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Onglet Branding */}
                <TabsContent value="branding">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Palette className="w-5 h-5 mr-2" />
                        Configuration du Branding
                      </CardTitle>
                      <CardDescription>
                        Personnalisez l'apparence de vos rapports
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Informations entreprise */}
                        <div className="space-y-4">
                          <h4 className="font-medium flex items-center">
                            <Building2 className="w-4 h-4 mr-2" />
                            Informations Entreprise
                          </h4>
                          
                          <div>
                            <Label htmlFor="company_name">Nom de l'entreprise</Label>
                            <Input
                              id="company_name"
                              value={brandingConfig.company_name}
                              onChange={(e) => handleBrandingChange('company_name', e.target.value)}
                              placeholder="Nom de votre entreprise"
                            />
                          </div>

                          <div>
                            <Label htmlFor="company_address">Adresse</Label>
                            <Textarea
                              id="company_address"
                              value={brandingConfig.company_address}
                              onChange={(e) => handleBrandingChange('company_address', e.target.value)}
                              placeholder="Adresse complète"
                              rows={3}
                            />
                          </div>

                          <div>
                            <Label htmlFor="company_phone">Téléphone</Label>
                            <Input
                              id="company_phone"
                              value={brandingConfig.company_phone}
                              onChange={(e) => handleBrandingChange('company_phone', e.target.value)}
                              placeholder="+33 1 23 45 67 89"
                            />
                          </div>

                          <div>
                            <Label htmlFor="company_email">Email</Label>
                            <Input
                              id="company_email"
                              type="email"
                              value={brandingConfig.company_email}
                              onChange={(e) => handleBrandingChange('company_email', e.target.value)}
                              placeholder="contact@entreprise.com"
                            />
                          </div>
                        </div>

                        {/* Apparence */}
                        <div className="space-y-4">
                          <h4 className="font-medium">Apparence</h4>
                          
                          <div>
                            <Label htmlFor="logo_upload">Logo de l'entreprise</Label>
                            <Input
                              id="logo_upload"
                              type="file"
                              accept="image/*"
                              onChange={handleLogoUpload}
                              className="mt-2"
                            />
                            {brandingConfig.logo_path && (
                              <div className="mt-2">
                                <img 
                                  src={brandingConfig.logo_path} 
                                  alt="Logo" 
                                  className="h-16 w-auto border rounded"
                                />
                              </div>
                            )}
                          </div>

                          <div className="grid grid-cols-3 gap-3">
                            <div>
                              <Label htmlFor="primary_color">Couleur principale</Label>
                              <Input
                                id="primary_color"
                                type="color"
                                value={brandingConfig.primary_color}
                                onChange={(e) => handleBrandingChange('primary_color', e.target.value)}
                              />
                            </div>
                            <div>
                              <Label htmlFor="secondary_color">Couleur secondaire</Label>
                              <Input
                                id="secondary_color"
                                type="color"
                                value={brandingConfig.secondary_color}
                                onChange={(e) => handleBrandingChange('secondary_color', e.target.value)}
                              />
                            </div>
                            <div>
                              <Label htmlFor="accent_color">Couleur d'accent</Label>
                              <Input
                                id="accent_color"
                                type="color"
                                value={brandingConfig.accent_color}
                                onChange={(e) => handleBrandingChange('accent_color', e.target.value)}
                              />
                            </div>
                          </div>

                          <div>
                            <Label htmlFor="font_family">Police</Label>
                            <Select 
                              value={brandingConfig.font_family} 
                              onValueChange={(value) => handleBrandingChange('font_family', value)}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="Arial">Arial</SelectItem>
                                <SelectItem value="Helvetica">Helvetica</SelectItem>
                                <SelectItem value="Times New Roman">Times New Roman</SelectItem>
                                <SelectItem value="Calibri">Calibri</SelectItem>
                                <SelectItem value="Georgia">Georgia</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          <div>
                            <Label htmlFor="header_text">Texte d'en-tête</Label>
                            <Input
                              id="header_text"
                              value={brandingConfig.header_text}
                              onChange={(e) => handleBrandingChange('header_text', e.target.value)}
                              placeholder="Texte personnalisé pour l'en-tête"
                            />
                          </div>

                          <div>
                            <Label htmlFor="footer_text">Texte de pied de page</Label>
                            <Input
                              id="footer_text"
                              value={brandingConfig.footer_text}
                              onChange={(e) => handleBrandingChange('footer_text', e.target.value)}
                              placeholder="Texte personnalisé pour le pied de page"
                            />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Onglet Paramètres */}
                <TabsContent value="settings">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Settings className="w-5 h-5 mr-2" />
                        Paramètres de Génération
                      </CardTitle>
                      <CardDescription>
                        Configurez les options de génération du rapport
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        <div>
                          <Label htmlFor="output_format">Format de sortie</Label>
                          <Select value={outputFormat} onValueChange={setOutputFormat}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="PDF">PDF</SelectItem>
                              <SelectItem value="Word">Word (.docx)</SelectItem>
                              <SelectItem value="Excel">Excel (.xlsx)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="p-4 bg-blue-50 rounded-lg">
                          <h4 className="font-medium text-blue-900 mb-2">Aperçu du Template</h4>
                          <div className="text-sm text-blue-800">
                            <p><strong>Nom:</strong> {selectedTemplate.name}</p>
                            <p><strong>Type:</strong> {selectedTemplate.template_type}</p>
                            <p><strong>Secteur:</strong> {selectedTemplate.sector}</p>
                            <p><strong>Sections:</strong> {selectedTemplate.sections.length}</p>
                            <p><strong>Formats supportés:</strong> {selectedTemplate.format_options?.join(', ')}</p>
                          </div>
                        </div>

                        <div className="flex space-x-2">
                          <Button variant="outline" className="flex-1">
                            <Eye className="w-4 h-4 mr-2" />
                            Aperçu
                          </Button>
                          <Button variant="outline" className="flex-1">
                            <Copy className="w-4 h-4 mr-2" />
                            Dupliquer Template
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Sélectionnez un template
                    </h3>
                    <p className="text-gray-600">
                      Choisissez un template dans la liste de gauche pour commencer
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportGenerator

