#!/usr/bin/python3

from collections import Counter
import json
import re
import matplotlib.pyplot as plt
import config
from script_AnalyzeRepos import results_base_dir, projects
import pandas as pd


plots_base_dir = config.ROOT_DIR + "/Resources/Output_typeErrors/"


ignored_warning_kinds = [
    "Undefined import [21]",
    "Undefined or invalid type [11]",
    "Undefined name [18]",
    "Undefined attribute [16]",
]


def read_results(name):
    with open(results_base_dir+name+".json") as fp:
        r = json.load(fp)
    return r


def get_results():
    project_to_history = {}
    latest_results = []
    for p in projects:
        try:
            p_results = read_results("history_"+p)
        except Exception as e:
            print(
                f"WARNING: Couldn't read results for {p}. Skipping this project.")
            continue
        project_to_history[p] = p_results
        latest_p_result = p_results[0]
        latest_p_result["project"] = p
        latest_results.append(latest_p_result)
    print(f"Read {len(project_to_history)} project histories")
    return project_to_history, pd.DataFrame(latest_results)


def count_filtered_warnings(kind_to_nb):
    total = 0
    for kind, nb in kind_to_nb.items():
        if kind not in ignored_warning_kinds:
            total += nb
    return total


def compute_more_columns(results):
    warnings = []
    for kind_to_nb in results["kind_to_nb"]:
        nb_warnings = count_filtered_warnings(kind_to_nb)
        warnings.append(nb_warnings)
    results["nb_filtered_warnings"] = warnings

    results["nb_types"] = results["nb_param_types"] + \
        results["nb_return_types"] + results["nb_variable_types"]


def plot_warnings_loc_evolution(p):
    results = read_results("history_"+p)
    dates = []
    locs = []
    warnings = []
    for r in reversed(results):
        date = r["commit_date"]
        date = date.split(" ")[0]
        dates.append(date)
        locs.append(r["loc"])
        nb_warnings = count_filtered_warnings(r["kind_to_nb"])
        warnings.append(nb_warnings)

    print(dates)
    print(warnings)
    print(locs)

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Date")
    plt.xticks(rotation=90)
    ax1.set_ylabel("Type warnings")
    ax1.plot(dates, warnings, label="Type warnings", marker="o")
    ax1.legend()
    ax1.set_ylim(bottom=0)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Lines of code")
    ax2.plot(dates, locs, label="Lines of code",
             linestyle="dashed", marker="x")
    ax2.legend()
    ax2.set_ylim(bottom=0)
    fig.tight_layout()
    ax1.set_title(f"Evolution of {p}")
    plt.savefig(plots_base_dir+"warnings_log_evolution_"+p+".pdf")
    plt.close()


def plot_kinds_of_errors(results):
    total_kind_to_nb = Counter()
    for kind_to_nb in results["kind_to_nb"]:
        total_kind_to_nb.update(Counter(kind_to_nb))

    kinds = []
    nbs = []
    kind_matcher = re.compile(r" \[.*")
    for kind, nb in total_kind_to_nb.most_common():
        if kind not in ignored_warning_kinds:
            kind = kind_matcher.sub("", kind)
            kinds.append(kind)
            nbs.append(nb)

    y_pos = range(len(kinds))
    plt.bar(y_pos, nbs, align='center', alpha=0.5)
    plt.xticks(y_pos, kinds)
    plt.xticks(rotation=90)
    plt.ylabel("Number of warnings")
    plt.title("Prevalence of kinds of type warnings")
    plt.tight_layout()
    plt.savefig(plots_base_dir+"kinds_of_warnings.pdf")
    plt.close()


def plot_errors_vs_loc(results):
    plt.plot(results["loc"], results["nb_filtered_warnings"], "o")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Lines of code")
    plt.ylabel("Number of warnings")
    plt.title("Type errors vs. code size")
    plt.tight_layout()
    plt.savefig(plots_base_dir+"errors_vs_loc.pdf")
    plt.close()


def plot_evolution_of_errors_vs_loc(project_to_history):
    for p, h in project_to_history.items():
        errors_per_loc = []
        for r in h:
            loc = r["loc"]
            nb_warnings = count_filtered_warnings(r["kind_to_nb"])
            if loc > 0:
                errors_per_loc.append(nb_warnings / loc)
            else:
                errors_per_loc.append(0)
        plt.plot(errors_per_loc)
    plt.xlabel("Time steps during version history")
    plt.ylabel("Type errors per lines of code")
    plt.tight_layout()
    plt.savefig(plots_base_dir+"errors_vs_loc_evolution.pdf")
    plt.close()


def plot_errors_vs_annotations(results):
    plt.plot(results["nb_types"], results["nb_filtered_warnings"], "o")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Type annotations")
    plt.ylabel("Number of warnings")
    plt.title("Type errors vs. annotations")
    plt.tight_layout()
    plt.savefig(plots_base_dir+"errors_vs_annotations.pdf")
    plt.close()


def plot_evolution_of_errors_vs_annotations(project_to_history):
    for p, h in project_to_history.items():
        errors_per_annotations = []
        for r in h:
            nb_annotations = r["nb_param_types"] + \
                r["nb_return_types"] + r["nb_variable_types"]
            nb_warnings = count_filtered_warnings(r["kind_to_nb"])
            if nb_annotations > 0:
                errors_per_annotations.append(nb_warnings / nb_annotations)
            else:
                errors_per_annotations.append(0)
        plt.plot(errors_per_annotations)

    plt.xlabel("Time steps during version history")
    plt.ylabel("Type errors per annotation")
    plt.ylim(0, 50)
    plt.tight_layout()
    plt.savefig(plots_base_dir+"errors_vs_annotations_evolution.pdf")
    plt.close()


def plot_evolution_of_avg_errors_vs_annotations(project_to_history):
    sum_at_step = [0.0] * 10
    for p, h in project_to_history.items():
        for step, r in enumerate(h[:10]):
            nb_annotations = r["nb_param_types"] + \
                r["nb_return_types"] + r["nb_variable_types"]
            nb_warnings = count_filtered_warnings(r["kind_to_nb"])
            if nb_annotations > 0:
                sum_at_step[step] += nb_warnings / nb_annotations
    avg_at_step = [s / len(project_to_history) for s in sum_at_step]
    plt.plot(avg_at_step)
    plt.xlabel("Time steps during version history")
    plt.ylabel("Type errors per annotation (avg. across projects)")
    plt.tight_layout()
    plt.savefig(plots_base_dir+"errors_vs_annotations_evolution_avg.pdf")
    plt.close()


def plot_per_project_evolution(project_to_history):
    plt.rcParams.update({'font.size': 16})
    for p, h in project_to_history.items():
        annotation_evol = []
        loc_evol = []
        for r in reversed(h[:10]):
            annotation_evol.append(r["nb_param_types"] +
                                   r["nb_return_types"] + r["nb_variable_types"])
            loc_evol.append(r["loc"])
        _, ax1 = plt.subplots()
        plt.xlabel(f"Time steps during version history of {p}")
        ax1.set_ylim(bottom=0, top=max(loc_evol)*1.05)
        line1 = ax1.plot(loc_evol, label="Lines of code (left)",
                         marker="o", color="blue")
        ax2 = ax1.twinx()
        ax2.set_ylim(bottom=0, top=max(max(annotation_evol)*1.05, 20))
        line2 = ax2.plot(
            annotation_evol, label="Type annotations (right)", marker="x", color="brown")
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        plt.legend(lines, labels)
        plt.tight_layout()
        plt.savefig(f"{plots_base_dir}per_project/{p}.pdf")
        plt.close()


def compute_stats_on_histories(project_to_history):
    print("\n------------------")
    print("Statistics on histories:")
    commits_total = 0
    commits_with_errors = 0
    for p, h in project_to_history.items():
        for r in h:
            commits_total += 1
            nb_warnings = count_filtered_warnings(r["kind_to_nb"])
            if nb_warnings > 0:
                commits_with_errors += 1
    print(f"  {commits_total} total commits")
    print(f"  {commits_with_errors} commits with errors ({round(commits_with_errors*100 / commits_total, 1)}%)")


def compute_stats_on_latest(results):
    print("\n------------------")
    print("Statistics on latest versions:")
    loc_total = results["loc"].sum()
    errors_total = results["nb_filtered_warnings"].sum()

    print(f"  {loc_total} total LoC in latest versions")
    print(f"  {errors_total} total errors in latest versions")
    print(f"  {round(errors_total / loc_total, 3)} errors per LoC, on average")

    corr_loc_errors = results["loc"].corr(results["nb_filtered_warnings"])
    print(f"  Correlation between errors and LoC: {corr_loc_errors}")
    corr_annotations_errors = results["nb_types"].corr(
        results["nb_filtered_warnings"])
    print(
        f"  Correlation between errors and annotations: {corr_annotations_errors}")


#Pure commits: Run on all
#Evolution of type errors vs type annotations: Run on 1/20 or 1/50
#Store raw output of mypy for later reuse

if __name__ == "__main__":
    project_to_history, latest_results = get_results()
    compute_more_columns(latest_results)

    plot_kinds_of_errors(latest_results)
    plot_errors_vs_loc(latest_results)
    plot_errors_vs_annotations(latest_results)

    plot_per_project_evolution(project_to_history)
    plot_evolution_of_errors_vs_annotations(project_to_history)
    plot_evolution_of_avg_errors_vs_annotations(project_to_history)
    plot_evolution_of_errors_vs_loc(project_to_history)

    compute_stats_on_latest(latest_results)
    compute_stats_on_histories(project_to_history)

    #    plot_warnings_loc_evolution(p)
