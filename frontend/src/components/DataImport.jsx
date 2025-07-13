import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  ArrowLeft,
  Download,
  Eye
} from 'lucide-react'

const DataImport = ({ user, projectId, onBack }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [importType, setImportType] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [importResult, setImportResult] = useState(null)
  const [previewData, setPreviewData] = useState(null)
  const [error, setError] = useState('')

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedFile(file)
      setError('')
      setImportResult(null)
      setPreviewData(null)
    }
  }

  const handlePreview = async () => {
    if (!selectedFile || !importType) {
      setError('Veuillez sélectionner un fichier et un type d\'import')
      return
    }

    setIsUploading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('import_type', importType)

    try {
      const response = await fetch('/api/data/preview', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      const result = await response.json()

      if (result.success) {
        setPreviewData(result)
      } else {
        setError(result.errors?.join(', ') || 'Erreur lors de la prévisualisation')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
    } finally {
      setIsUploading(false)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || !importType || !projectId) {
      setError('Informations manquantes pour l\'import')
      return
    }

    setIsUploading(true)
    setError('')
    setUploadProgress(0)

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('import_type', importType)
    formData.append('audit_project_id', projectId)

    try {
      // Simuler la progression
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch('/api/data/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      const result = await response.json()

      if (result.success) {
        setImportResult(result)
        setSelectedFile(null)
        setImportType('')
      } else {
        setError(result.errors?.join(', ') || 'Erreur lors de l\'import')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 2000)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* En-tête */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour au Dashboard
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Importation de Données</h1>
              <p className="text-gray-600">Importez vos fichiers comptables pour analyse</p>
            </div>
          </div>
        </div>

        {/* Formulaire d'import */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Upload className="w-5 h-5 mr-2" />
              Sélection du fichier
            </CardTitle>
            <CardDescription>
              Formats supportés : Excel (.xlsx, .xls), CSV, JSON. Taille maximum : 50MB
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Sélection du type d'import */}
            <div className="space-y-2">
              <Label htmlFor="import-type">Type de données</Label>
              <Select value={importType} onValueChange={setImportType}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionnez le type de données à importer" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="balance">Balance générale</SelectItem>
                  <SelectItem value="journal">Écritures de journal</SelectItem>
                  <SelectItem value="grand_livre">Grand livre</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Sélection du fichier */}
            <div className="space-y-2">
              <Label htmlFor="file-upload">Fichier à importer</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  id="file-upload"
                  type="file"
                  accept=".xlsx,.xls,.csv,.json"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-600">
                    Cliquez pour sélectionner un fichier ou glissez-déposez
                  </p>
                </label>
              </div>
            </div>

            {/* Informations du fichier sélectionné */}
            {selectedFile && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-900">{selectedFile.name}</p>
                      <p className="text-sm text-blue-600">{formatFileSize(selectedFile.size)}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handlePreview}
                      disabled={!importType || isUploading}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      Prévisualiser
                    </Button>
                    <Button 
                      onClick={handleUpload}
                      disabled={!importType || isUploading}
                    >
                      <Upload className="w-4 h-4 mr-1" />
                      Importer
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Barre de progression */}
            {isUploading && uploadProgress > 0 && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progression de l'import</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="w-full" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Prévisualisation des données */}
        {previewData && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Prévisualisation des données</CardTitle>
              <CardDescription>
                {previewData.total_rows} lignes détectées • Format : {previewData.file_format}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Colonnes détectées */}
                <div>
                  <h4 className="font-medium mb-2">Colonnes détectées :</h4>
                  <div className="flex flex-wrap gap-2">
                    {previewData.columns_detected?.map((column, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                      >
                        {column}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Aperçu des données */}
                {previewData.preview_data && previewData.preview_data.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Aperçu des premières lignes :</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full border border-gray-200 rounded">
                        <thead className="bg-gray-50">
                          <tr>
                            {Object.keys(previewData.preview_data[0]).map((key, index) => (
                              <th key={index} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {previewData.preview_data.slice(0, 5).map((row, index) => (
                            <tr key={index} className="border-t">
                              {Object.values(row).map((value, cellIndex) => (
                                <td key={cellIndex} className="px-3 py-2 text-sm text-gray-900">
                                  {String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Résumé de validation */}
                {previewData.validation_summary && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                      <p className="text-sm font-medium text-yellow-800">Avertissements</p>
                      <p className="text-lg font-bold text-yellow-900">
                        {previewData.validation_summary.rows_with_warnings}
                      </p>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded p-3">
                      <p className="text-sm font-medium text-red-800">Erreurs</p>
                      <p className="text-lg font-bold text-red-900">
                        {previewData.validation_summary.rows_with_errors}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Résultat de l'import */}
        {importResult && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-green-700">
                <CheckCircle className="w-5 h-5 mr-2" />
                Import réussi
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {importResult.summary?.rows_processed || 0}
                    </p>
                    <p className="text-sm text-gray-600">Lignes traitées</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-yellow-600">
                      {importResult.summary?.rows_with_warnings || 0}
                    </p>
                    <p className="text-sm text-gray-600">Avertissements</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">
                      {importResult.summary?.rows_with_errors || 0}
                    </p>
                    <p className="text-sm text-gray-600">Erreurs</p>
                  </div>
                </div>

                {importResult.validation_errors && importResult.validation_errors.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Détails des erreurs :</h4>
                    <div className="max-h-40 overflow-y-auto space-y-1">
                      {importResult.validation_errors.slice(0, 10).map((error, index) => (
                        <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                          Ligne {error.row}: {error.error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-center">
                  <Button onClick={onBack}>
                    Retour au Dashboard
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Messages d'erreur */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  )
}

export default DataImport

