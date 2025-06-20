import json
from pathlib import Path
import networkx as nx
import sys

# Add the repository_analysis directory to the path to import the analyzer
sys.path.append(str(Path(__file__).resolve().parent.parent / "repository_analysis"))

try:
    from dependency_analyzer import DependencyAnalyzer
    from metadata_extractor import MetadataExtractor
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "Please ensure that dependency_analyzer.py and metadata_extractor.py are accessible."
    )
    sys.exit(1)


def build_dependency_graph(
    project_root: Path, files_to_analyze: list[str]
) -> nx.DiGraph:
    """
    Builds a dependency graph for the specified files.
    """
    metadata_list = []
    extractor = MetadataExtractor(str(project_root))

    for file_path_str in files_to_analyze:
        file_path = Path(file_path_str)
        if file_path.exists() and file_path.is_file():
            try:
                metadata = extractor.extract_metadata(str(file_path))
                metadata_list.append(metadata)
            except Exception as e:
                print(f"Could not extract metadata for {file_path}: {e}")

    analyzer = DependencyAnalyzer(project_root)
    dep_graph = analyzer.analyze_dependencies(metadata_list)

    # Convert to a NetworkX graph for topological sort
    # We only care about internal dependencies for movement ordering
    nx_graph = nx.DiGraph()
    for edge in dep_graph.edges:
        if edge.dependency_type == "internal":
            source = str(edge.source_file)

            # Resolve the target module to a file path
            target_module_path = analyzer._resolve_python_module(
                edge.target_module, edge.source_file
            )
            if not target_module_path:
                target_module_path = analyzer._resolve_js_module(
                    edge.target_module, edge.source_file
                )

            if target_module_path:
                target = str(target_module_path)
                if source in files_to_analyze and target in files_to_analyze:
                    nx_graph.add_edge(source, target)

    return nx_graph


def main():
    """
    Orders the file movements based on dependencies.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    map_path = project_root / "migration-map.json"
    plan_path = project_root / "migration-plan.json"

    with open(map_path, "r") as f:
        migration_map = json.load(f)

    files_to_move = list(migration_map.keys())

    print("Building dependency graph...")
    dep_graph = build_dependency_graph(project_root, files_to_move)

    try:
        # Topological sort gives us an order where dependencies come before dependents
        # We want to move files with FEWER dependencies first, so we move leaf nodes up.
        # The standard topological sort of G gives dependents first.
        # To move files that are dependencies first, we can reverse the graph.
        reversed_graph = dep_graph.reverse()
        ordered_files = list(nx.topological_sort(reversed_graph))

        # Add files that are not in the graph (no internal dependencies)
        files_in_graph = set(ordered_files)
        standalone_files = [f for f in files_to_move if f not in files_in_graph]

        # The final order is standalone files first, then the topologically sorted files.
        final_order = standalone_files + ordered_files

    except nx.NetworkXUnfeasible:
        print("Error: A cycle was detected in the dependency graph.")
        print(
            "Cannot determine a safe movement order. Please fix the circular dependencies."
        )

        # Find and print the cycle
        cycle = nx.find_cycle(dep_graph)
        print("Cycle found:", " -> ".join(cycle))

        sys.exit(1)

    migration_plan = []
    for file_path in final_order:
        if file_path in migration_map:
            migration_plan.append(
                {"source": file_path, "target": migration_map[file_path]}
            )

    with open(plan_path, "w") as f:
        json.dump(migration_plan, f, indent=2)

    print(
        f"Generated migration plan with {len(migration_plan)} movements at: {plan_path}"
    )


if __name__ == "__main__":
    main()
