import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { 
  Crown, 
  Zap, 
  Gift, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Star,
  TrendingUp,
  Shield,
  Sparkles
} from 'lucide-react'

const SubscriptionManager = ({ user, onBack }) => {
  const [subscriptionStatus, setSubscriptionStatus] = useState(null)
  const [plans, setPlans] = useState({})
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState(false)

  useEffect(() => {
    fetchSubscriptionStatus()
    fetchPlans()
  }, [])

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await fetch(`/api/subscription/status?user_id=${user.id}`)
      const data = await response.json()
      if (data.success) {
        setSubscriptionStatus(data.data)
      }
    } catch (error) {
      console.error('Erreur lors de la récupération du statut:', error)
    }
  }

  const fetchPlans = async () => {
    try {
      const response = await fetch('/api/subscription/plans')
      const data = await response.json()
      if (data.success) {
        setPlans(data.data)
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des plans:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpgrade = async (planType) => {
    setUpgrading(true)
    try {
      // Simulation du paiement
      const paymentResponse = await fetch('/api/subscription/simulate-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          plan_type: planType,
          amount: plans[planType]?.price || 0
        })
      })

      const paymentData = await paymentResponse.json()
      
      if (paymentData.success) {
        // Actualiser le statut après le paiement
        await fetchSubscriptionStatus()
        alert(`🎉 Félicitations ! Votre abonnement ${plans[planType]?.name} a été activé avec succès !`)
      } else {
        alert(`Erreur lors du paiement: ${paymentData.message}`)
      }
    } catch (error) {
      console.error('Erreur lors de la mise à niveau:', error)
      alert('Erreur lors de la mise à niveau. Veuillez réessayer.')
    } finally {
      setUpgrading(false)
    }
  }

  const getStatusBadge = () => {
    if (!subscriptionStatus) return null

    const { subscription_type, status } = subscriptionStatus

    if (subscription_type === 'free') {
      return <Badge variant="secondary" className="bg-gray-100 text-gray-800">Gratuit</Badge>
    } else if (subscription_type === 'monthly') {
      return <Badge variant="default" className="bg-blue-100 text-blue-800">Mensuel</Badge>
    } else if (subscription_type === 'yearly') {
      return <Badge variant="default" className="bg-purple-100 text-purple-800">Annuel</Badge>
    }
  }

  const getProgressPercentage = () => {
    if (!subscriptionStatus || subscriptionStatus.max_audits === -1) return 100
    return (subscriptionStatus.audits_used / subscriptionStatus.max_audits) * 100
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement de vos informations d'abonnement...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Button 
              variant="ghost" 
              onClick={onBack}
              className="mb-4 hover:bg-white/50"
            >
              ← Retour au Dashboard
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Abonnements</h1>
            <p className="text-gray-600 mt-2">Gérez votre abonnement et débloquez tout le potentiel de ZenCompta</p>
          </div>
          {getStatusBadge()}
        </div>

        {/* Statut actuel */}
        {subscriptionStatus && (
          <Card className="mb-8 border-2 border-blue-200 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Crown className="h-6 w-6 text-yellow-500" />
                Votre Abonnement Actuel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Plan Actuel</h3>
                  <p className="text-2xl font-bold text-blue-600">
                    {subscriptionStatus.plan_details?.name || 'Gratuit'}
                  </p>
                  {subscriptionStatus.subscription_type !== 'free' && (
                    <p className="text-sm text-gray-600 mt-1">
                      {subscriptionStatus.days_until_expiry !== null 
                        ? `Expire dans ${subscriptionStatus.days_until_expiry} jours`
                        : 'Actif'
                      }
                    </p>
                  )}
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Audits Utilisés</h3>
                  {subscriptionStatus.max_audits === -1 ? (
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-purple-500" />
                      <span className="text-2xl font-bold text-purple-600">Illimité</span>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-2xl font-bold text-gray-900">
                          {subscriptionStatus.audits_used} / {subscriptionStatus.max_audits}
                        </span>
                        <span className="text-sm text-gray-600">
                          {subscriptionStatus.remaining_audits} restants
                        </span>
                      </div>
                      <Progress 
                        value={getProgressPercentage()} 
                        className="h-2"
                      />
                    </div>
                  )}
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Statut</h3>
                  <div className="flex items-center gap-2">
                    {subscriptionStatus.can_perform_audit ? (
                      <>
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="text-green-600 font-semibold">Actif</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="h-5 w-5 text-red-500" />
                        <span className="text-red-600 font-semibold">Limite atteinte</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Plans d'abonnement */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Plan Gratuit */}
          {plans.free && (
            <Card className="relative border-2 border-gray-200 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gift className="h-6 w-6 text-gray-500" />
                  {plans.free.name}
                </CardTitle>
                <CardDescription>Découvrez ZenCompta</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold text-gray-900">Gratuit</div>
                  <div className="text-sm text-gray-600">Pour toujours</div>
                </div>
                
                <ul className="space-y-3 mb-6">
                  {plans.free.features?.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>

                {subscriptionStatus?.subscription_type === 'free' ? (
                  <Button disabled className="w-full">
                    Plan Actuel
                  </Button>
                ) : (
                  <Button variant="outline" disabled className="w-full">
                    Plan de Base
                  </Button>
                )}
              </CardContent>
            </Card>
          )}

          {/* Plan Mensuel */}
          {plans.monthly && (
            <Card className="relative border-2 border-blue-300 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-6 w-6 text-blue-500" />
                  {plans.monthly.name}
                </CardTitle>
                <CardDescription>Flexibilité maximale</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold text-blue-600">
                    {plans.monthly.price?.toLocaleString()} FCFA
                  </div>
                  <div className="text-sm text-gray-600">par mois</div>
                </div>
                
                <ul className="space-y-3 mb-6">
                  {plans.monthly.features?.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>

                {subscriptionStatus?.subscription_type === 'monthly' ? (
                  <Button disabled className="w-full">
                    Plan Actuel
                  </Button>
                ) : (
                  <Button 
                    onClick={() => handleUpgrade('monthly')}
                    disabled={upgrading}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {upgrading ? 'Traitement...' : 'Choisir ce Plan'}
                  </Button>
                )}
              </CardContent>
            </Card>
          )}

          {/* Plan Annuel */}
          {plans.yearly && (
            <Card className="relative border-2 border-purple-300 bg-white/80 backdrop-blur-sm">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-purple-600 text-white px-4 py-1">
                  <Star className="h-3 w-3 mr-1" />
                  RECOMMANDÉ
                </Badge>
              </div>
              
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Crown className="h-6 w-6 text-purple-500" />
                  {plans.yearly.name}
                </CardTitle>
                <CardDescription>Meilleure valeur</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold text-purple-600">
                    {plans.yearly.price?.toLocaleString()} FCFA
                  </div>
                  <div className="text-sm text-gray-600">par an</div>
                  <div className="text-sm text-green-600 font-semibold mt-1">
                    Économisez 133.000 FCFA !
                  </div>
                </div>
                
                <ul className="space-y-3 mb-6">
                  {plans.yearly.features?.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>

                {subscriptionStatus?.subscription_type === 'yearly' ? (
                  <Button disabled className="w-full">
                    Plan Actuel
                  </Button>
                ) : (
                  <Button 
                    onClick={() => handleUpgrade('yearly')}
                    disabled={upgrading}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    {upgrading ? 'Traitement...' : 'Choisir ce Plan'}
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Avantages de la mise à niveau */}
        {subscriptionStatus?.subscription_type === 'free' && (
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-blue-600" />
                Pourquoi Passer Premium ?
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">🚀 Gains de Productivité</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Gain de temps de 85% sur vos audits</li>
                    <li>• Capacité d'audit multipliée par 6</li>
                    <li>• Précision de 99.7% grâce à l'IA</li>
                    <li>• ROI moyen de 400% dès le premier mois</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">💎 Fonctionnalités Exclusives</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Visualisations 3D spectaculaires</li>
                    <li>• Templates professionnels illimités</li>
                    <li>• IA avancée pour détection d'anomalies</li>
                    <li>• Support VIP prioritaire</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Garanties */}
        <Card className="mt-8 bg-green-50 border-2 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-green-600" />
              Nos Garanties
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <Clock className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-semibold text-gray-900">Garantie 60 jours</h3>
                <p className="text-sm text-gray-600">Satisfait ou remboursé</p>
              </div>
              
              <div className="text-center">
                <Shield className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-semibold text-gray-900">Sécurité totale</h3>
                <p className="text-sm text-gray-600">Paiement 100% sécurisé</p>
              </div>
              
              <div className="text-center">
                <Sparkles className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-semibold text-gray-900">Support VIP</h3>
                <p className="text-sm text-gray-600">Assistance prioritaire</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SubscriptionManager

