"""
Example usage of WhoScored Data Extractor

This script demonstrates how to extract data from all WhoScored sections
for a given match ID.
"""

from whoscored_extractor import WhoScoredExtractor


def main():
    # Initialize the extractor
    # Set headless=False to see the browser in action
    extractor = WhoScoredExtractor(headless=True, browser_type="firefox")

    # Example match ID (you can change this to any valid WhoScored match ID)
    # To find a match ID, visit WhoScored.com, navigate to a match, and extract the ID from the URL
    # Example URL: https://www.whoscored.com/Matches/1234567/Live/...
    # The match ID would be: 1234567
    match_id = 1716104  # Example: A recent match

    print("WhoScored Data Extractor")
    print("=" * 70)
    print(f"Match ID: {match_id}")
    print("=" * 70)
    print("\nThis will extract data from all sections:")
    print("  1. Preview - Pre-match information and predictions")
    print("  2. Head to Head - Historical matchup data")
    print("  3. Betting - Odds and betting information")
    print("  4. Match Centre - Match statistics and events")
    print("  5. Match Report - Detailed match events and player data")
    print("\n" + "=" * 70 + "\n")

    # Extract data from all sections
    all_data = extractor.extract_all_sections(match_id)

    # Save to JSON file
    output_file = f"whoscored_match_{match_id}_all_data.json"
    extractor.save_to_json(all_data, output_file)

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)

    for section_name, section_data in all_data['sections'].items():
        status = "✓ SUCCESS" if section_data['success'] else "✗ FAILED"
        print(f"{section_name.upper():20} - {status}")

        if not section_data['success']:
            print(f"  Error: {section_data.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)
    print(f"Complete data saved to: {output_file}")
    print("=" * 70)


def extract_single_section():
    """Example of extracting data from a single section."""
    extractor = WhoScoredExtractor(headless=True)
    match_id = 1716104

    # Extract only Match Report (Live) data
    match_report = extractor.extract_match_report(match_id)

    if match_report['success']:
        print("Match Report extracted successfully!")

        # Access the data
        data = match_report['data']

        # Example: Access match centre data if available
        if 'matchCentreData' in data:
            match_info = data['matchCentreData']
            print(f"\nHome Team: {match_info.get('home', {}).get('name', 'N/A')}")
            print(f"Away Team: {match_info.get('away', {}).get('name', 'N/A')}")

            # Access events
            if 'events' in match_info:
                print(f"Total Events: {len(match_info['events'])}")

        # Save to file
        extractor.save_to_json(match_report, f"match_{match_id}_report.json")
    else:
        print(f"Failed to extract Match Report: {match_report['error']}")


if __name__ == "__main__":
    # Run the main extraction
    main()

    # Uncomment to run single section extraction example
    # extract_single_section()
