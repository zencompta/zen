"""
Service de détection automatique du type de fichier comptable
Analyse les fichiers pour déterminer leur type et format comptable
"""

import os
import pandas as pd
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes
import chardet


class FileDetector:
    """Service de détection automatique du type de fichier comptable"""
    
    def __init__(self):
        self.supported_formats = {
            'FEC': {
                'description': 'Fichier des Écritures Comptables',
                'extensions': ['.txt', '.csv'],
                'required_columns': ['JournalCode', 'JournalLib', 'EcritureNum', 'EcritureDate', 'CompteNum', 'CompteLib', 'CompAuxNum', 'CompAuxLib', 'PieceRef', 'PieceDate', 'EcritureLib', 'Debit', 'Credit', 'EcritureLet', 'DateLet', 'ValidDate', 'Montantdevise', 'Idevise'],
                'separator': '|'
            },
            'BALANCE': {
                'description': 'Balance comptable',
                'extensions': ['.xlsx', '.xls', '.csv'],
                'required_columns': ['compte', 'libelle', 'debit', 'credit'],
                'optional_columns': ['solde', 'mouvement_debit', 'mouvement_credit']
            },
            'GRAND_LIVRE': {
                'description': 'Grand livre comptable',
                'extensions': ['.xlsx', '.xls', '.csv'],
                'required_columns': ['date', 'piece', 'libelle', 'debit', 'credit'],
                'optional_columns': ['compte', 'journal']
            },
            'JOURNAL': {
                'description': 'Journal comptable',
                'extensions': ['.xlsx', '.xls', '.csv'],
                'required_columns': ['date', 'piece', 'compte', 'libelle', 'debit', 'credit'],
                'optional_columns': ['journal', 'reference']
            },
            'FACTURE': {
                'description': 'Facture',
                'extensions': ['.pdf', '.jpg', '.jpeg', '.png'],
                'keywords': ['facture', 'invoice', 'montant', 'tva', 'ht', 'ttc']
            },
            'RELEVE_BANCAIRE': {
                'description': 'Relevé bancaire',
                'extensions': ['.pdf', '.csv', '.xlsx'],
                'keywords': ['banque', 'compte', 'solde', 'debit', 'credit', 'virement']
            }
        }
    
    def detect_file_type(self, file_path: str) -> Dict:
        """
        Détecte automatiquement le type d'un fichier comptable
        
        Args:
            file_path: Chemin vers le fichier à analyser
            
        Returns:
            Dict contenant les informations de détection
        """
        result = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'detected_type': None,
            'confidence': 0.0,
            'format_details': {},
            'encoding': None,
            'separator': None,
            'errors': []
        }
        
        try:
            # Vérifier l'existence du fichier
            if not os.path.exists(file_path):
                result['errors'].append(f"Fichier non trouvé: {file_path}")
                return result
            
            # Détecter l'extension
            file_extension = Path(file_path).suffix.lower()
            result['extension'] = file_extension
            
            # Détecter le type MIME
            mime_type, _ = mimetypes.guess_type(file_path)
            result['mime_type'] = mime_type
            
            # Détecter l'encodage pour les fichiers texte
            if file_extension in ['.txt', '.csv']:
                result['encoding'] = self._detect_encoding(file_path)
            
            # Analyser selon le type de fichier
            if file_extension in ['.csv', '.txt']:
                result = self._analyze_csv_file(file_path, result)
            elif file_extension in ['.xlsx', '.xls']:
                result = self._analyze_excel_file(file_path, result)
            elif file_extension in ['.pdf']:
                result = self._analyze_pdf_file(file_path, result)
            elif file_extension in ['.jpg', '.jpeg', '.png']:
                result = self._analyze_image_file(file_path, result)
            else:
                result['errors'].append(f"Type de fichier non supporté: {file_extension}")
            
        except Exception as e:
            result['errors'].append(f"Erreur lors de l'analyse: {str(e)}")
        
        return result
    
    def _detect_encoding(self, file_path: str) -> str:
        """Détecte l'encodage d'un fichier texte"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Lire les premiers 10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'
    
    def _analyze_csv_file(self, file_path: str, result: Dict) -> Dict:
        """Analyse un fichier CSV/TXT"""
        try:
            encoding = result.get('encoding', 'utf-8')
            
            # Tester différents séparateurs
            separators = ['|', ';', ',', '\t']
            best_separator = None
            max_columns = 0
            
            for sep in separators:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding=encoding, nrows=5)
                    if len(df.columns) > max_columns:
                        max_columns = len(df.columns)
                        best_separator = sep
                except:
                    continue
            
            if best_separator:
                result['separator'] = best_separator
                df = pd.read_csv(file_path, sep=best_separator, encoding=encoding, nrows=100)
                result['columns'] = list(df.columns)
                result['row_count'] = len(df)
                
                # Détecter le type de fichier comptable
                detected_type, confidence = self._detect_accounting_type(df.columns, df)
                result['detected_type'] = detected_type
                result['confidence'] = confidence
                
                if detected_type:
                    result['format_details'] = self.supported_formats.get(detected_type, {})
            
        except Exception as e:
            result['errors'].append(f"Erreur analyse CSV: {str(e)}")
        
        return result
    
    def _analyze_excel_file(self, file_path: str, result: Dict) -> Dict:
        """Analyse un fichier Excel"""
        try:
            # Lire la première feuille
            df = pd.read_excel(file_path, nrows=100)
            result['columns'] = list(df.columns)
            result['row_count'] = len(df)
            
            # Détecter le type de fichier comptable
            detected_type, confidence = self._detect_accounting_type(df.columns, df)
            result['detected_type'] = detected_type
            result['confidence'] = confidence
            
            if detected_type:
                result['format_details'] = self.supported_formats.get(detected_type, {})
                
        except Exception as e:
            result['errors'].append(f"Erreur analyse Excel: {str(e)}")
        
        return result
    
    def _analyze_pdf_file(self, file_path: str, result: Dict) -> Dict:
        """Analyse un fichier PDF"""
        try:
            # Pour l'instant, classification basique basée sur le nom et la taille
            file_name = result['file_name'].lower()
            
            if any(keyword in file_name for keyword in ['facture', 'invoice']):
                result['detected_type'] = 'FACTURE'
                result['confidence'] = 0.7
            elif any(keyword in file_name for keyword in ['releve', 'bancaire', 'bank']):
                result['detected_type'] = 'RELEVE_BANCAIRE'
                result['confidence'] = 0.7
            else:
                result['detected_type'] = 'DOCUMENT_PDF'
                result['confidence'] = 0.5
                
            result['format_details'] = self.supported_formats.get(result['detected_type'], {})
            
        except Exception as e:
            result['errors'].append(f"Erreur analyse PDF: {str(e)}")
        
        return result
    
    def _analyze_image_file(self, file_path: str, result: Dict) -> Dict:
        """Analyse un fichier image"""
        try:
            file_name = result['file_name'].lower()
            
            if any(keyword in file_name for keyword in ['facture', 'invoice']):
                result['detected_type'] = 'FACTURE'
                result['confidence'] = 0.6
            else:
                result['detected_type'] = 'DOCUMENT_IMAGE'
                result['confidence'] = 0.5
                
        except Exception as e:
            result['errors'].append(f"Erreur analyse image: {str(e)}")
        
        return result
    
    def _detect_accounting_type(self, columns: List[str], df: pd.DataFrame) -> Tuple[Optional[str], float]:
        """
        Détecte le type de fichier comptable basé sur les colonnes
        
        Returns:
            Tuple (type_detecté, niveau_de_confiance)
        """
        columns_lower = [col.lower().strip() for col in columns]
        
        # Vérifier chaque type de fichier comptable
        for file_type, config in self.supported_formats.items():
            if 'required_columns' not in config:
                continue
                
            required_cols = [col.lower() for col in config['required_columns']]
            optional_cols = [col.lower() for col in config.get('optional_columns', [])]
            
            # Calculer le score de correspondance
            matches = 0
            total_required = len(required_cols)
            
            for req_col in required_cols:
                if any(req_col in col or col in req_col for col in columns_lower):
                    matches += 1
            
            # Bonus pour les colonnes optionnelles
            optional_matches = 0
            for opt_col in optional_cols:
                if any(opt_col in col or col in opt_col for col in columns_lower):
                    optional_matches += 1
            
            # Calculer la confiance
            confidence = matches / total_required if total_required > 0 else 0
            if optional_matches > 0:
                confidence += (optional_matches / len(optional_cols)) * 0.2
            
            # Vérifications spécifiques pour FEC
            if file_type == 'FEC' and confidence > 0.7:
                # Vérifier le format des dates et montants
                if self._validate_fec_format(df):
                    confidence = min(confidence + 0.1, 1.0)
            
            if confidence > 0.6:  # Seuil de confiance minimum
                return file_type, min(confidence, 1.0)
        
        return None, 0.0
    
    def _validate_fec_format(self, df: pd.DataFrame) -> bool:
        """Valide le format spécifique du FEC"""
        try:
            # Vérifier le format des dates (YYYYMMDD)
            date_columns = ['EcritureDate', 'PieceDate', 'DateLet', 'ValidDate']
            for col in date_columns:
                if col in df.columns:
                    sample_dates = df[col].dropna().head(5)
                    for date_val in sample_dates:
                        if isinstance(date_val, str) and len(date_val) == 8:
                            try:
                                int(date_val)  # Doit être numérique
                            except:
                                return False
            
            # Vérifier les montants (format décimal)
            amount_columns = ['Debit', 'Credit', 'Montantdevise']
            for col in amount_columns:
                if col in df.columns:
                    sample_amounts = df[col].dropna().head(5)
                    for amount in sample_amounts:
                        try:
                            float(str(amount).replace(',', '.'))
                        except:
                            return False
            
            return True
        except:
            return False
    
    def get_supported_formats(self) -> Dict:
        """Retourne la liste des formats supportés"""
        return self.supported_formats
    
    def validate_file_structure(self, file_path: str, expected_type: str) -> Dict:
        """
        Valide la structure d'un fichier selon un type attendu
        
        Args:
            file_path: Chemin vers le fichier
            expected_type: Type attendu (FEC, BALANCE, etc.)
            
        Returns:
            Dict avec les résultats de validation
        """
        result = {
            'is_valid': False,
            'expected_type': expected_type,
            'missing_columns': [],
            'extra_columns': [],
            'format_errors': [],
            'recommendations': []
        }
        
        if expected_type not in self.supported_formats:
            result['format_errors'].append(f"Type non supporté: {expected_type}")
            return result
        
        # Détecter le type réel
        detection_result = self.detect_file_type(file_path)
        
        if detection_result['detected_type'] == expected_type:
            result['is_valid'] = True
        else:
            config = self.supported_formats[expected_type]
            required_cols = config.get('required_columns', [])
            actual_cols = detection_result.get('columns', [])
            
            # Identifier les colonnes manquantes
            for req_col in required_cols:
                if not any(req_col.lower() in col.lower() for col in actual_cols):
                    result['missing_columns'].append(req_col)
            
            # Recommandations
            if result['missing_columns']:
                result['recommendations'].append(
                    f"Ajouter les colonnes manquantes: {', '.join(result['missing_columns'])}"
                )
            
            if detection_result['detected_type']:
                result['recommendations'].append(
                    f"Le fichier semble être de type '{detection_result['detected_type']}' "
                    f"avec une confiance de {detection_result['confidence']:.2f}"
                )
        
        return result

