import pandas as pd
from utils.logger import get_logger

class DataProcessor:
    def __init__(self, agent):
        self.agent = agent
        self.logger = get_logger("DataProcessor")

    def load_data(self, file_path):
        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'csv':
                df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='warn')
            elif file_extension in ['xls', 'xlsx', 'xlsm']:
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_extension == 'json':
                df = pd.read_json(file_path)
            elif file_extension == 'parquet':
                df = pd.read_parquet(file_path)
            elif file_extension == 'txt':
                # Try different delimiters
                for delimiter in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(file_path, sep=delimiter, encoding='utf-8')
                        if len(df.columns) > 1:  # Found correct delimiter
                            break
                    except:
                        continue
                else:  # If no delimiter worked
                    raise ValueError("Could not determine delimiter for txt file")
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            if df.empty:
                raise ValueError("The loaded dataframe is empty")

            self.logger.info(f"Data loaded successfully from {file_path}")
            self.logger.info(f"Shape of loaded data: {df.shape}")
            return df

        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    if file_extension == 'csv':
                        df = pd.read_csv(file_path, encoding=encoding)
                        self.logger.info(f"Successfully read with {encoding} encoding")
                        return df
                except:
                    continue
            raise ValueError("Could not read file with any supported encoding")
            
        except Exception as e:
            self.logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise

    def process_data(self, df, custom_code=None):
        try:
            if custom_code:
                # Create a namespace with necessary imports and variables
                namespace = {
                    'df': df.copy(),  # Work with a copy of the DataFrame
                    'pd': pd,
                    'np': __import__('numpy'),
                    'LabelEncoder': __import__('sklearn.preprocessing').preprocessing.LabelEncoder,
                    'StandardScaler': __import__('sklearn.preprocessing').preprocessing.StandardScaler,
                    'MinMaxScaler': __import__('sklearn.preprocessing').preprocessing.MinMaxScaler
                }
                
                try:
                    # Execute the custom code in the prepared namespace
                    exec(custom_code, namespace)
                    cleaned_df = namespace['df']
                    
                    # Verify if the operation actually changed the DataFrame
                    if cleaned_df.equals(df):
                        self.logger.info("Operation resulted in no changes to the data")
                        return df
                    
                    # Verify if all required columns are still present
                    if not all(col in cleaned_df.columns for col in df.columns):
                        missing_cols = set(df.columns) - set(cleaned_df.columns)
                        self.logger.info(f"Operation attempted to remove columns: {missing_cols}")
                        if any(col not in df.columns for col in missing_cols):
                            # If trying to remove non-existent columns, return original
                            return df
                    
                    return cleaned_df
                    
                except Exception as code_error:
                    # Use CodeExecutor to handle the error
                    fixed_code = self.agent.code_executor._handle_error(
                        code_error,
                        custom_code,
                        df
                    )
                    
                    # Try executing the fixed code
                    namespace['df'] = df.copy()  # Reset DataFrame
                    exec(fixed_code, namespace)
                    cleaned_df = namespace['df']
                    
                    # Verify the fixed code result
                    if cleaned_df.equals(df):
                        return df
                    
                    return cleaned_df
                
                self.logger.info("Custom code processing completed")
            else:
                cleaned_df = self.agent.process_data(df)
                self.logger.info("Data processing completed")
            return cleaned_df
        except Exception as e:
            self.logger.error(f"Error during processing: {e}")
            return df  # Return original DataFrame instead of raising exception

    def save_data(self, df, output_file):
        try:
            df.to_csv(output_file, index=False)
            self.logger.info(f"Processed data saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            raise

    def log_processing_history(self):
        for entry in self.agent.data_processor.cleaning_history.get_all_entries():
            self.logger.info(f"Step {entry.iteration}: {entry.instruction}")