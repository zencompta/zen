"""
Service OCR pour la reconnaissance de documents scannés
Extraction automatique de données à partir d'images et de PDFs
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import base64
from datetime import datetime
import tempfile

# Pour une implémentation complète, nous utiliserions des bibliothèques comme:
# import pytesseract
# from PIL import Image
# import pdf2image
# import cv2
# import numpy as np

class OCRService:
    """Service de reconnaissance optique de caractères pour documents comptables"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        self.document_templates = {
            'FACTURE': {
                'patterns': {
                    'numero_facture': [
                        r'(?:facture|invoice|n°|no\.?|number)\s*:?\s*([A-Z0-9\-/]+)',
                        r'(?:fact|inv)\s*[:\-]?\s*([A-Z0-9\-/]+)'
                    ],
                    'date': [
                        r'(?:date|du|le)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                        r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
                    ],
                    'montant_ht': [
                        r'(?:total|montant)\s*(?:ht|hors\s*taxe)\s*:?\s*([0-9\s,\.]+)',
                        r'(?:sous[\-\s]*total|st)\s*:?\s*([0-9\s,\.]+)'
                    ],
                    'montant_tva': [
                        r'(?:tva|taxe)\s*:?\s*([0-9\s,\.]+)',
                        r'(?:vat|tax)\s*:?\s*([0-9\s,\.]+)'
                    ],
                    'montant_ttc': [
                        r'(?:total|montant)\s*(?:ttc|toutes\s*taxes)\s*:?\s*([0-9\s,\.]+)',
                        r'(?:total\s*général|grand\s*total)\s*:?\s*([0-9\s,\.]+)'
                    ],
                    'fournisseur': [
                        r'(?:de|from|société|company)\s*:?\s*([A-Za-z\s\-\.]+)',
                        r'^([A-Z][A-Za-z\s\-\.]+)(?:\n|$)'
                    ],
                    'siret': [
                        r'(?:siret|siren)\s*:?\s*([0-9\s]+)',
                        r'([0-9]{14})'
                    ]
                },
                'required_fields': ['numero_facture', 'date', 'montant_ttc'],
                'optional_fields': ['montant_ht', 'montant_tva', 'fournisseur', 'siret']
            },
            'RELEVE_BANCAIRE': {
                'patterns': {
                    'numero_compte': [
                        r'(?:compte|account|n°)\s*:?\s*([0-9\s\-]+)',
                        r'([0-9]{10,})'
                    ],
                    'periode': [
                        r'(?:période|period|du)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s*(?:au|to)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
                    ],
                    'solde_initial': [
                        r'(?:solde\s*initial|opening\s*balance)\s*:?\s*([0-9\s,\.\-]+)'
                    ],
                    'solde_final': [
                        r'(?:solde\s*final|closing\s*balance)\s*:?\s*([0-9\s,\.\-]+)'
                    ],
                    'banque': [
                        r'(?:banque|bank)\s*:?\s*([A-Za-z\s\-\.]+)'
                    ]
                },
                'required_fields': ['numero_compte', 'periode'],
                'optional_fields': ['solde_initial', 'solde_final', 'banque']
            },
            'CHEQUE': {
                'patterns': {
                    'numero_cheque': [
                        r'(?:chèque|cheque|n°)\s*:?\s*([0-9]+)'
                    ],
                    'montant': [
                        r'(?:montant|amount)\s*:?\s*([0-9\s,\.]+)',
                        r'€\s*([0-9\s,\.]+)'
                    ],
                    'date': [
                        r'(?:le|date)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
                    ],
                    'beneficiaire': [
                        r'(?:à|to|payable\s*à)\s*:?\s*([A-Za-z\s\-\.]+)'
                    ]
                },
                'required_fields': ['numero_cheque', 'montant'],
                'optional_fields': ['date', 'beneficiaire']
            }
        }
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extrait le texte d'une image en utilisant OCR
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Dict contenant le texte extrait et les métadonnées
        """
        result = {
            'success': False,
            'text': '',
            'confidence': 0.0,
            'language': 'fr',
            'processing_time': 0.0,
            'errors': []
        }
        
        try:
            start_time = datetime.now()
            
            # Vérifier l'existence du fichier
            if not os.path.exists(image_path):
                result['errors'].append(f"Fichier non trouvé: {image_path}")
                return result
            
            # Vérifier l'extension
            file_extension = Path(image_path).suffix.lower()
            if file_extension not in self.supported_formats:
                result['errors'].append(f"Format non supporté: {file_extension}")
                return result
            
            # Simulation d'extraction OCR (en production, utiliser pytesseract)
            # Dans une vraie implémentation:
            # image = Image.open(image_path)
            # text = pytesseract.image_to_string(image, lang='fra')
            # confidence = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Pour la démonstration, simuler l'extraction
            result['text'] = self._simulate_ocr_extraction(image_path)
            result['confidence'] = 0.85  # Confiance simulée
            result['success'] = True
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['errors'].append(f"Erreur OCR: {str(e)}")
        
        return result
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extrait le texte d'un PDF (texte natif ou OCR sur images)
        
        Args:
            pdf_path: Chemin vers le PDF
            
        Returns:
            Dict contenant le texte extrait
        """
        result = {
            'success': False,
            'text': '',
            'pages': [],
            'is_scanned': False,
            'processing_time': 0.0,
            'errors': []
        }
        
        try:
            start_time = datetime.now()
            
            # Vérifier l'existence du fichier
            if not os.path.exists(pdf_path):
                result['errors'].append(f"Fichier non trouvé: {pdf_path}")
                return result
            
            # En production, utiliser PyPDF2 ou pdfplumber pour le texte natif
            # et pdf2image + pytesseract pour les PDFs scannés
            
            # Simulation d'extraction
            result['text'] = self._simulate_pdf_extraction(pdf_path)
            result['pages'] = [{'page': 1, 'text': result['text']}]
            result['is_scanned'] = 'scan' in os.path.basename(pdf_path).lower()
            result['success'] = True
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['errors'].append(f"Erreur extraction PDF: {str(e)}")
        
        return result
    
    def analyze_document(self, file_path: str, document_type: Optional[str] = None) -> Dict:
        """
        Analyse un document et extrait les informations structurées
        
        Args:
            file_path: Chemin vers le document
            document_type: Type de document attendu (FACTURE, RELEVE_BANCAIRE, etc.)
            
        Returns:
            Dict contenant les données extraites et structurées
        """
        result = {
            'success': False,
            'document_type': document_type,
            'detected_type': None,
            'extracted_data': {},
            'confidence_scores': {},
            'validation_errors': [],
            'processing_time': 0.0,
            'errors': []
        }
        
        try:
            start_time = datetime.now()
            
            # Extraire le texte selon le type de fichier
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                extraction_result = self.extract_text_from_pdf(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                extraction_result = self.extract_text_from_image(file_path)
            else:
                result['errors'].append(f"Type de fichier non supporté: {file_extension}")
                return result
            
            if not extraction_result['success']:
                result['errors'].extend(extraction_result['errors'])
                return result
            
            text = extraction_result['text']
            
            # Détecter le type de document si non spécifié
            if not document_type:
                document_type = self._detect_document_type(text)
                result['detected_type'] = document_type
            
            if document_type and document_type in self.document_templates:
                # Extraire les données selon le template
                extracted_data, confidence_scores = self._extract_structured_data(
                    text, document_type
                )
                result['extracted_data'] = extracted_data
                result['confidence_scores'] = confidence_scores
                
                # Valider les données extraites
                validation_errors = self._validate_extracted_data(
                    extracted_data, document_type
                )
                result['validation_errors'] = validation_errors
                
                result['success'] = True
            else:
                result['errors'].append(f"Type de document non supporté: {document_type}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['errors'].append(f"Erreur analyse document: {str(e)}")
        
        return result
    
    def _simulate_ocr_extraction(self, image_path: str) -> str:
        """Simule l'extraction OCR d'une image"""
        filename = os.path.basename(image_path).lower()
        
        if 'facture' in filename or 'invoice' in filename:
            return """
            FACTURE N° FAC-2024-001
            Date: 15/01/2024
            
            Société ABC
            123 Rue de la Paix
            75001 Paris
            SIRET: 12345678901234
            
            Prestation de service
            Montant HT: 1000,00 €
            TVA 20%: 200,00 €
            Total TTC: 1200,00 €
            """
        elif 'releve' in filename or 'bank' in filename:
            return """
            RELEVÉ BANCAIRE
            Compte N°: 12345678901
            Période: du 01/01/2024 au 31/01/2024
            
            Banque Exemple
            Solde initial: 5000,00 €
            Solde final: 4800,00 €
            """
        else:
            return "Texte extrait par OCR - contenu générique"
    
    def _simulate_pdf_extraction(self, pdf_path: str) -> str:
        """Simule l'extraction de texte d'un PDF"""
        filename = os.path.basename(pdf_path).lower()
        
        if 'facture' in filename:
            return """
            FACTURE ÉLECTRONIQUE
            Numéro: FACT-2024-0156
            Date d'émission: 20/01/2024
            
            Fournisseur: Entreprise XYZ
            Client: Société Client
            
            Détail des prestations:
            - Service 1: 800,00 € HT
            - Service 2: 300,00 € HT
            
            Sous-total HT: 1100,00 €
            TVA 20%: 220,00 €
            Total TTC: 1320,00 €
            """
        else:
            return "Contenu PDF extrait"
    
    def _detect_document_type(self, text: str) -> Optional[str]:
        """Détecte automatiquement le type de document basé sur le contenu"""
        text_lower = text.lower()
        
        # Mots-clés pour chaque type de document
        keywords = {
            'FACTURE': ['facture', 'invoice', 'montant', 'tva', 'ttc', 'ht'],
            'RELEVE_BANCAIRE': ['relevé', 'bancaire', 'compte', 'solde', 'banque'],
            'CHEQUE': ['chèque', 'cheque', 'payable', 'bénéficiaire']
        }
        
        scores = {}
        for doc_type, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            scores[doc_type] = score
        
        # Retourner le type avec le score le plus élevé
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] >= 2:  # Seuil minimum
                return best_type
        
        return None
    
    def _extract_structured_data(self, text: str, document_type: str) -> Tuple[Dict, Dict]:
        """Extrait les données structurées selon le type de document"""
        template = self.document_templates.get(document_type, {})
        patterns = template.get('patterns', {})
        
        extracted_data = {}
        confidence_scores = {}
        
        for field, field_patterns in patterns.items():
            best_match = None
            best_confidence = 0.0
            
            for pattern in field_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if match.groups():
                        value = match.group(1).strip()
                        # Calculer la confiance basée sur la position et la clarté
                        confidence = self._calculate_field_confidence(match, text, field)
                        
                        if confidence > best_confidence:
                            best_match = value
                            best_confidence = confidence
            
            if best_match:
                extracted_data[field] = self._clean_extracted_value(best_match, field)
                confidence_scores[field] = best_confidence
        
        return extracted_data, confidence_scores
    
    def _calculate_field_confidence(self, match, text: str, field: str) -> float:
        """Calcule la confiance d'une extraction de champ"""
        base_confidence = 0.7
        
        # Bonus si le champ est près du début du document
        position_ratio = match.start() / len(text)
        if position_ratio < 0.3:
            base_confidence += 0.1
        
        # Bonus pour certains patterns spécifiques
        if field in ['montant_ttc', 'numero_facture']:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _clean_extracted_value(self, value: str, field: str) -> str:
        """Nettoie et formate une valeur extraite"""
        value = value.strip()
        
        # Nettoyage spécifique selon le type de champ
        if 'montant' in field or 'solde' in field:
            # Nettoyer les montants
            value = re.sub(r'[^\d,\.\-]', '', value)
            value = value.replace(',', '.')
        elif 'date' in field:
            # Normaliser les dates
            value = re.sub(r'[^\d\/\-\.]', '', value)
        elif 'numero' in field:
            # Nettoyer les numéros
            value = re.sub(r'[^\w\-\/]', '', value)
        
        return value
    
    def _validate_extracted_data(self, data: Dict, document_type: str) -> List[str]:
        """Valide les données extraites selon le type de document"""
        errors = []
        template = self.document_templates.get(document_type, {})
        required_fields = template.get('required_fields', [])
        
        # Vérifier les champs obligatoires
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Champ obligatoire manquant: {field}")
        
        # Validations spécifiques
        if 'date' in data:
            if not self._validate_date_format(data['date']):
                errors.append(f"Format de date invalide: {data['date']}")
        
        if any('montant' in key for key in data.keys()):
            for key, value in data.items():
                if 'montant' in key and not self._validate_amount_format(value):
                    errors.append(f"Format de montant invalide: {key} = {value}")
        
        return errors
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Valide le format d'une date"""
        date_patterns = [
            r'\d{1,2}\/\d{1,2}\/\d{4}',
            r'\d{1,2}\-\d{1,2}\-\d{4}',
            r'\d{1,2}\.\d{1,2}\.\d{4}'
        ]
        
        return any(re.match(pattern, date_str) for pattern in date_patterns)
    
    def _validate_amount_format(self, amount_str: str) -> bool:
        """Valide le format d'un montant"""
        try:
            # Essayer de convertir en float
            float(amount_str.replace(',', '.'))
            return True
        except:
            return False
    
    def get_supported_document_types(self) -> List[str]:
        """Retourne la liste des types de documents supportés"""
        return list(self.document_templates.keys())
    
    def batch_process_documents(self, file_paths: List[str], document_type: Optional[str] = None) -> List[Dict]:
        """
        Traite plusieurs documents en lot
        
        Args:
            file_paths: Liste des chemins vers les fichiers
            document_type: Type de document (optionnel)
            
        Returns:
            Liste des résultats d'analyse
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.analyze_document(file_path, document_type)
                result['file_path'] = file_path
                results.append(result)
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'success': False,
                    'errors': [f"Erreur traitement: {str(e)}"]
                })
        
        return results

