import argparse
from pathlib import Path
from .smart_file_system import SmartFileSystem
import json
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Mindful Organizer - Smart File System CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Index command
    index_parser = subparsers.add_parser("index", help="Index files in a directory")
    index_parser.add_argument("directory", help="Directory to index")
    index_parser.add_argument(
        "--db", 
        default="file_index.db",
        help="Database file path (default: file_index.db)"
    )

    # Cluster command
    cluster_parser = subparsers.add_parser("cluster", help="Cluster indexed files")
    cluster_parser.add_argument(
        "--db", 
        default="file_index.db",
        help="Database file path (default: file_index.db)"
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate cluster report")
    report_parser.add_argument(
        "--db", 
        default="file_index.db",
        help="Database file path (default: file_index.db)"
    )
    report_parser.add_argument(
        "--output", 
        default="cluster_report.json",
        help="Output file path (default: cluster_report.json)"
    )
    report_parser.add_argument(
        "--format",
        choices=["json", "txt"],
        default="json",
        help="Output format (default: json)"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for similar files")
    search_parser.add_argument("query", help="Search query text")
    search_parser.add_argument(
        "--db", 
        default="file_index.db",
        help="Database file path (default: file_index.db)"
    )
    search_parser.add_argument(
        "--top-k", 
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )

    args = parser.parse_args()

    sfs = SmartFileSystem(db_path=args.db)

    try:
        if args.command == "index":
            result = sfs.index_directory(args.directory)
            print(f"Indexed {result['files_indexed']} files in {result['time_elapsed']:.2f}s")
            
        elif args.command == "cluster":
            result = sfs.cluster_files()
            print(f"Found {result['clusters_found']} clusters in {result['time_elapsed']:.2f}s")
            
        elif args.command == "report":
            result = sfs.generate_report(args.output, args.format)
            print(f"Report saved to {args.output}")
            
        elif args.command == "search":
            results = sfs.get_similar_files(args.query, args.top_k)
            print("Similar files:")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['path']} (similarity: {r['similarity']:.3f})")
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
