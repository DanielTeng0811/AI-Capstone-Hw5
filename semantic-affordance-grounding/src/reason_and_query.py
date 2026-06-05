from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL, XSD


ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
IMPORTS_DIR = ONTOLOGY_DIR / "imports"
QUERIES_DIR = ROOT / "queries"
RESULTS_DIR = ROOT / "results"

CAP = Namespace("https://hcis.io/ontology/aicapstone/2026/")
GXX = Namespace("https://hcis.io/ontology/aicapstone/2026/group01/")


def load_graph() -> Graph:
    graph = Graph()
    graph.bind("cap", CAP)
    graph.bind("g01", GXX)
    graph.bind("owl", OWL)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("xsd", XSD)

    for path in [
        IMPORTS_DIR / "course-affordance.ttl",
        IMPORTS_DIR / "course-alignment.ttl",
        ONTOLOGY_DIR / "group-ontology.ttl",
    ]:
        graph.parse(path, format="turtle")
    return graph


def subclasses_of(graph: Graph, cls: URIRef) -> set[URIRef]:
    subclasses = {cls}
    changed = True
    while changed:
        changed = False
        for subject, _, obj in graph.triples((None, RDFS.subClassOf, None)):
            if isinstance(subject, URIRef) and obj in subclasses and subject not in subclasses:
                subclasses.add(subject)
                changed = True
    return subclasses


def has_some_values_restriction(
    graph: Graph,
    cls: URIRef,
    prop: URIRef,
    filler_classes: set[URIRef],
) -> bool:
    for restriction in graph.objects(cls, RDFS.subClassOf):
        if not isinstance(restriction, BNode):
            continue
        if (restriction, RDF.type, OWL.Restriction) not in graph:
            continue
        if (restriction, OWL.onProperty, prop) not in graph:
            continue
        for filler in graph.objects(restriction, OWL.someValuesFrom):
            if filler in filler_classes:
                return True
    return False


def materialize_graspability(graph: Graph) -> list[URIRef]:
    grasping_classes = subclasses_of(graph, CAP.GraspingAffordance)
    physical_classes = subclasses_of(graph, CAP.PhysicalObject)

    graspable_types = {
        cls
        for cls in physical_classes
        if has_some_values_restriction(graph, cls, CAP.hasAffordance, grasping_classes)
    }

    inferred: list[URIRef] = []
    for obj, _, cls in graph.triples((None, RDF.type, None)):
        if not isinstance(obj, URIRef) or cls not in graspable_types:
            continue

        graph.add((obj, RDF.type, CAP.PhysicalObject))
        graph.add((obj, RDF.type, CAP.GraspableObject))

        affordance = URIRef(str(obj) + "GraspingAffordance")
        graph.add((obj, CAP.hasAffordance, affordance))
        graph.add((affordance, RDF.type, CAP.GraspingAffordance))
        graph.add((affordance, RDFS.label, Literal(f"inferred grasping affordance for {obj.split('/')[-1]}", lang="en")))
        graph.add((
            affordance,
            RDFS.comment,
            Literal(
                "Materialized by the homework rule layer because this object's asserted class has an owl:someValuesFrom restriction to cap:GraspingAffordance.",
                lang="en",
            ),
        ))
        inferred.append(obj)

    return sorted(set(inferred), key=str)


def write_query_results(graph: Graph) -> str:
    query = (QUERIES_DIR / "graspable_objects.rq").read_text(encoding="utf-8")
    rows = list(graph.query(query))

    lines = [
        "Inferred graspable objects",
        "==========================",
        "",
        "Query: queries/graspable_objects.rq",
        "Data: ontology/inferred-results.ttl",
        "",
        f"{'object':<24} {'name':<18} {'label':<18} role",
        "-" * 95,
    ]
    for row in rows:
        obj = row.obj.split("/")[-1]
        name = str(row.name) if row.name else ""
        label = str(row.label) if row.label else ""
        role = row.role.split("/")[-1] if row.role else ""
        lines.append(f"{obj:<24} {name:<18} {label:<18} {role}")

    output = "\n".join(lines) + "\n"
    (RESULTS_DIR / "graspable_objects_output.txt").write_text(output, encoding="utf-8")
    return output


def main() -> None:
    graph = load_graph()
    inferred = materialize_graspability(graph)
    graph.serialize(ONTOLOGY_DIR / "inferred-results.ttl", format="turtle")
    output = write_query_results(graph)
    print(output)
    print(dedent(f"""
        Materialized {len(inferred)} cap:GraspableObject assertions:
        {', '.join(obj.split('/')[-1] for obj in inferred)}
    """).strip())


if __name__ == "__main__":
    main()
