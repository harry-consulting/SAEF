from analyzer.analyzers import AnalyzerActualDataset, AnalyzerExpectedDataset, AnalyzerComparisonDataset
from analyzer.tasks.util import create_dataset_session_meta_data


def task_analyze_dataset(dataset_session_pk):
    try:
        analyzer = AnalyzerActualDataset(dataset_session_pk)
        actual_dataset, actual_dataset_dict = analyzer.execute()

        analyzer = AnalyzerExpectedDataset(dataset_session_pk, actual_dataset)
        expected_dataset, expected_dataset_dict = analyzer.execute()

        analyzer = AnalyzerComparisonDataset(actual_dataset, expected_dataset)
        comparison_dataset_dict = analyzer.execute()

        create_dataset_session_meta_data(comparison_dataset_dict["degree_of_change"], dataset_session_pk)

        return {'actual': actual_dataset_dict, 'comparison': comparison_dataset_dict}
    except Exception as e:
        return {'error': str(e), 'type': str(type(e))}


