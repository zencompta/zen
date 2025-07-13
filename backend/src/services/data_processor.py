import pandas as pd
import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Any
import openpyxl
from io import BytesIO
import csv

class DataProcessor:
    """Service pour traiter et valider les données comptables importées"""
    
    def __init__(self):
        self.supported_formats = ['xlsx', 'xls', 'csv', 'json']
        self.required_columns = {
            'balance': ['account_number', 'account_name', 'debit_amount', 'credit_amount'],
            'journal': ['entry_date', 'account_number', 'description', 'debit_amount', 'credit_amount'],
            'grand_livre': ['entry_date', 'account_number', 'description', 'debit_amount', 'credit_amount', 'piece_number']
        }
    
    def detect_file_format(self, file_content: bytes, filename: str) -> str:
        """Détecte le format du fichier basé sur l'extension et le contenu"""
        extension = filename.lower().split('.')[-1]
        
        if extension in ['xlsx', 'xls']:
            return 'excel'
        elif extension == 'csv':
            return 'csv'
        elif extension == 'json':
            return 'json'
        else:
            raise ValueError(f"Format de fichier non supporté: {extension}")
    
    def extract_data_from_excel(self, file_content: bytes) -> pd.DataFrame:
        """Extrait les données d'un fichier Excel"""
        try:
            # Essayer de lire avec pandas
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            return df
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier Excel: {str(e)}")
    
    def extract_data_from_csv(self, file_content: bytes, encoding='utf-8') -> pd.DataFrame:
        """Extrait les données d'un fichier CSV"""
        try:
            # Essayer différents encodages si nécessaire
            encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
            
            for enc in encodings:
                try:
                    content_str = file_content.decode(enc)
                    # Détecter le délimiteur
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(content_str[:1024]).delimiter
                    
                    df = pd.read_csv(BytesIO(file_content), delimiter=delimiter, encoding=enc)
                    return df
                except (UnicodeDecodeError, pd.errors.EmptyDataError):
                    continue
            
            raise ValueError("Impossible de décoder le fichier CSV")
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier CSV: {str(e)}")
    
    def extract_data_from_json(self, file_content: bytes) -> pd.DataFrame:
        """Extrait les données d'un fichier JSON"""
        try:
            json_data = json.loads(file_content.decode('utf-8'))
            
            # Si c'est une liste d'objets
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            # Si c'est un objet avec une clé contenant les données
            elif isinstance(json_data, dict):
                # Chercher la clé qui contient les données (souvent 'data', 'records', etc.)
                data_keys = ['data', 'records', 'entries', 'items']
                data_found = False
                
                for key in data_keys:
                    if key in json_data and isinstance(json_data[key], list):
                        df = pd.DataFrame(json_data[key])
                        data_found = True
                        break
                
                if not data_found:
                    # Essayer de convertir directement l'objet
                    df = pd.DataFrame([json_data])
            else:
                raise ValueError("Structure JSON non supportée")
            
            return df
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier JSON: {str(e)}")
    
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise les noms de colonnes pour faciliter le mapping"""
        # Dictionnaire de mapping des noms de colonnes courantes
        column_mapping = {
            # Numéro de compte
            'compte': 'account_number',
            'numero_compte': 'account_number',
            'n_compte': 'account_number',
            'account': 'account_number',
            'code_compte': 'account_number',
            
            # Nom du compte
            'libelle': 'account_name',
            'libelle_compte': 'account_name',
            'nom_compte': 'account_name',
            'intitule': 'account_name',
            'designation': 'account_name',
            
            # Montants débit
            'debit': 'debit_amount',
            'montant_debit': 'debit_amount',
            'solde_debiteur': 'debit_amount',
            
            # Montants crédit
            'credit': 'credit_amount',
            'montant_credit': 'credit_amount',
            'solde_crediteur': 'credit_amount',
            
            # Date
            'date': 'entry_date',
            'date_ecriture': 'entry_date',
            'date_operation': 'entry_date',
            
            # Description
            'libelle_ecriture': 'description',
            'description': 'description',
            'objet': 'description',
            'motif': 'description',
            
            # Numéro de pièce
            'piece': 'piece_number',
            'numero_piece': 'piece_number',
            'n_piece': 'piece_number',
            'reference': 'piece_number',
            
            # Journal
            'journal': 'journal_code',
            'code_journal': 'journal_code',
            'type_journal': 'journal_code'
        }
        
        # Normaliser les noms de colonnes (minuscules, sans espaces)
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Appliquer le mapping
        df = df.rename(columns=column_mapping)
        
        return df
    
    def validate_data_structure(self, df: pd.DataFrame, import_type: str) -> Tuple[bool, List[str]]:
        """Valide la structure des données selon le type d'import"""
        errors = []
        
        if import_type not in self.required_columns:
            errors.append(f"Type d'import non supporté: {import_type}")
            return False, errors
        
        required_cols = self.required_columns[import_type]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            errors.append(f"Colonnes manquantes: {', '.join(missing_cols)}")
        
        # Vérifier que le DataFrame n'est pas vide
        if df.empty:
            errors.append("Le fichier ne contient aucune donnée")
        
        return len(errors) == 0, errors
    
    def clean_and_validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """Nettoie et valide les données ligne par ligne"""
        validation_errors = []
        
        # Copier le DataFrame pour éviter les modifications sur l'original
        cleaned_df = df.copy()
        
        # Nettoyer les montants
        for col in ['debit_amount', 'credit_amount']:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].apply(self._clean_amount)
        
        # Nettoyer les numéros de compte
        if 'account_number' in cleaned_df.columns:
            cleaned_df['account_number'] = cleaned_df['account_number'].apply(self._clean_account_number)
        
        # Nettoyer les dates
        if 'entry_date' in cleaned_df.columns:
            cleaned_df['entry_date'] = pd.to_datetime(cleaned_df['entry_date'], errors='coerce')
        
        # Valider ligne par ligne
        for index, row in cleaned_df.iterrows():
            row_errors = self._validate_row(row, index)
            validation_errors.extend(row_errors)
        
        return cleaned_df, validation_errors
    
    def _clean_amount(self, value) -> float:
        """Nettoie et convertit un montant en float"""
        if pd.isna(value) or value == '':
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Supprimer les espaces et caractères non numériques sauf . et ,
            cleaned = re.sub(r'[^\d.,-]', '', str(value))
            
            # Gérer les formats français (virgule comme séparateur décimal)
            if ',' in cleaned and '.' in cleaned:
                # Format: 1.234,56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Format: 1234,56
                cleaned = cleaned.replace(',', '.')
            
            try:
                return float(cleaned) if cleaned else 0.0
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _clean_account_number(self, value) -> str:
        """Nettoie un numéro de compte"""
        if pd.isna(value):
            return ''
        
        # Convertir en string et supprimer les espaces
        cleaned = str(value).strip()
        
        # Supprimer les caractères non alphanumériques sauf les tirets
        cleaned = re.sub(r'[^a-zA-Z0-9-]', '', cleaned)
        
        return cleaned
    
    def _validate_row(self, row: pd.Series, row_index: int) -> List[Dict]:
        """Valide une ligne de données"""
        errors = []
        
        # Vérifier le numéro de compte
        if 'account_number' in row and (pd.isna(row['account_number']) or row['account_number'] == ''):
            errors.append({
                'row': row_index + 1,
                'column': 'account_number',
                'error': 'Numéro de compte manquant',
                'severity': 'error'
            })
        
        # Vérifier les montants
        if 'debit_amount' in row and 'credit_amount' in row:
            debit = row['debit_amount'] if not pd.isna(row['debit_amount']) else 0
            credit = row['credit_amount'] if not pd.isna(row['credit_amount']) else 0
            
            if debit == 0 and credit == 0:
                errors.append({
                    'row': row_index + 1,
                    'column': 'amounts',
                    'error': 'Aucun montant saisi (débit et crédit à zéro)',
                    'severity': 'warning'
                })
            
            if debit != 0 and credit != 0:
                errors.append({
                    'row': row_index + 1,
                    'column': 'amounts',
                    'error': 'Montant en débit ET en crédit (inhabituel)',
                    'severity': 'warning'
                })
        
        # Vérifier la date si présente
        if 'entry_date' in row and pd.isna(row['entry_date']):
            errors.append({
                'row': row_index + 1,
                'column': 'entry_date',
                'error': 'Date invalide ou manquante',
                'severity': 'warning'
            })
        
        return errors
    
    def generate_mapping_suggestions(self, df: pd.DataFrame, import_type: str) -> Dict[str, str]:
        """Génère des suggestions de mapping automatique des colonnes"""
        suggestions = {}
        required_cols = self.required_columns.get(import_type, [])
        
        for required_col in required_cols:
            # Chercher la colonne la plus proche
            best_match = None
            best_score = 0
            
            for df_col in df.columns:
                score = self._calculate_column_similarity(df_col, required_col)
                if score > best_score and score > 0.5:  # Seuil de similarité
                    best_score = score
                    best_match = df_col
            
            if best_match:
                suggestions[required_col] = best_match
        
        return suggestions
    
    def _calculate_column_similarity(self, col1: str, col2: str) -> float:
        """Calcule la similarité entre deux noms de colonnes"""
        # Normaliser les noms
        col1_norm = col1.lower().replace('_', '').replace(' ', '').replace('-', '')
        col2_norm = col2.lower().replace('_', '').replace(' ', '').replace('-', '')
        
        # Vérifier si l'un contient l'autre
        if col1_norm in col2_norm or col2_norm in col1_norm:
            return 0.8
        
        # Calculer la similarité de Jaccard (simple)
        set1 = set(col1_norm)
        set2 = set(col2_norm)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0
    
    def apply_column_mapping(self, df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Applique un mapping de colonnes personnalisé"""
        # Inverser le mapping pour pandas rename
        reverse_mapping = {v: k for k, v in mapping.items() if v in df.columns}
        
        return df.rename(columns=reverse_mapping)
    
    def process_file(self, file_content: bytes, filename: str, import_type: str, 
                    custom_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Traite un fichier complet et retourne les résultats"""
        try:
            # 1. Détecter le format
            file_format = self.detect_file_format(file_content, filename)
            
            # 2. Extraire les données
            if file_format == 'excel':
                df = self.extract_data_from_excel(file_content)
            elif file_format == 'csv':
                df = self.extract_data_from_csv(file_content)
            elif file_format == 'json':
                df = self.extract_data_from_json(file_content)
            else:
                raise ValueError(f"Format non supporté: {file_format}")
            
            # 3. Normaliser les noms de colonnes
            df = self.normalize_column_names(df)
            
            # 4. Appliquer le mapping personnalisé si fourni
            if custom_mapping:
                df = self.apply_column_mapping(df, custom_mapping)
            
            # 5. Valider la structure
            is_valid, structure_errors = self.validate_data_structure(df, import_type)
            
            if not is_valid:
                return {
                    'success': False,
                    'errors': structure_errors,
                    'data': None,
                    'suggestions': self.generate_mapping_suggestions(df, import_type)
                }
            
            # 6. Nettoyer et valider les données
            cleaned_df, validation_errors = self.clean_and_validate_data(df)
            
            # 7. Convertir en format JSON pour stockage
            data_records = cleaned_df.to_dict('records')
            
            return {
                'success': True,
                'data': data_records,
                'validation_errors': validation_errors,
                'rows_processed': len(cleaned_df),
                'rows_with_errors': len([e for e in validation_errors if e['severity'] == 'error']),
                'rows_with_warnings': len([e for e in validation_errors if e['severity'] == 'warning']),
                'columns_detected': list(df.columns),
                'file_format': file_format
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'data': None
            }

