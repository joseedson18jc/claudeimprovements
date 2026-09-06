#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3] [--json]
       python search.py "<query>" --design-system [-p "Project Name"] [-f ascii|markdown|json | --json]

Domains: style, prompt, color, chart, landing, product, ux, typography, icons, react, web
Stacks: html-tailwind, react, nextjs, vue, nuxtjs, nuxt-ui, svelte, swiftui, react-native, flutter, shadcn
(the authoritative lists are CSV_CONFIG and AVAILABLE_STACKS in core.py)
"""

import argparse
import json
from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack
from design_system import generate_design_system, OUTPUT_FORMATS


def non_negative_int(value: str) -> int:
    """argparse type: an integer >= 0 (a negative slice bound would silently drop results)."""
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"must be >= 0, got {number}")
    return number


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    if result.get("stack"):
        output.append("## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
    else:
        output.append("## UI Pro Max Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")
    output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")

    for i, row in enumerate(result['results'], 1):
        output.append(f"### Result {i}")
        for key, value in row.items():
            value_str = str(value)
            if len(value_str) > 300:
                value_str = value_str[:300] + "..."
            output.append(f"- **{key}:** {value_str}")
        output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help=f"Stack-specific search ({', '.join(AVAILABLE_STACKS)})")
    parser.add_argument("--max-results", "-n", type=non_negative_int, default=MAX_RESULTS, help=f"Max results, >= 0 (default: {MAX_RESULTS})")
    parser.add_argument("--json", action="store_true", help="Output as JSON (applies to every mode, including --design-system)")
    # Design system generation
    parser.add_argument("--design-system", "-ds", action="store_true", help="Generate complete design system recommendation")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for design system output")
    parser.add_argument("--format", "-f", choices=list(OUTPUT_FORMATS), default="ascii", help="Output format for design system (--json is shorthand for -f json)")

    args = parser.parse_args()

    # Design system takes priority
    if args.design_system:
        output_format = "json" if args.json else args.format
        print(generate_design_system(args.query, args.project_name, output_format))
    # Stack search
    elif args.stack:
        result = search_stack(args.query, args.stack, args.max_results)
        print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else format_output(result))
    # Domain search
    else:
        result = search(args.query, args.domain, args.max_results)
        print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else format_output(result))
