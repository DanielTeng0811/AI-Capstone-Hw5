# Homework 5: Ontology-based Semantic Grounding

## Project Information

Project title: Semantic Affordance Grounding for Cup Stacking and Baseline Task Objects

Group: Group 1

Members: 李享 (110350011), 鍾翊琦 (112550210), 鄧皓澤 (112652046), 呂泰廷 (112652030), 白詩愷 (109550202)

## Selected Task

The main final-project task is cup stacking: a learned robot policy should move the blue cup onto the pink cup. This homework repository adds a semantic grounding layer for that task while also modeling the baseline objects required by the assignment:

- cup stacking: blue cup and pink cup;
- cutlery arrangement: knife, fork, and plate;
- toy block collection: toy blocks and basket.

## Repository Structure

```text
semantic-affordance-grounding/
|-- README.md
|-- report.md
|-- ontology/
|   |-- group-ontology.ttl
|   |-- inferred-results.ttl
|   `-- imports/
|       |-- course-affordance.ttl
|       `-- course-alignment.ttl
|-- queries/
|   |-- graspable_objects.rq
|   `-- task_objects.rq
|-- results/
|   |-- graspable_objects_output.txt
|   |-- screenshots/
|   |   |-- ontology_visualization_check.png
|   |   `-- query_output_terminal.png
|   `-- widoco/
|       `-- doc/
|           |-- index-en.html
|           `-- webvowl/
|-- src/
|   `-- reason_and_query.py
|-- widoco_portege/
|   |-- p.png
|   `-- w*.png
`-- requirements.txt
```

## Authored and Imported Ontologies

`ontology/group-ontology.ttl` is the group-authored ontology. It defines the group namespace, task individuals, object instances, labels, comments, and the `cap:GraspableObject` reasoning target from the homework specification.

`ontology/imports/course-affordance.ttl` and `ontology/imports/course-alignment.ttl` are imported course resources. The `course-affordance.ttl` file is the updated course ontology from the course GitHub repository.

## Namespace Policy

The shared course namespace is:

```ttl
@prefix cap: <https://hcis.io/ontology/aicapstone/2026/> .
```

The group namespace is:

```ttl
@prefix g01: <https://hcis.io/ontology/aicapstone/2026/group01/> .
```

Course-level classes and properties use `cap:`. Group 1 authored tasks, objects, and local individuals use `g01:`.

## Modeled Objects and Affordances

| Object | Type | Task role | Main affordance source | Inferred graspable? |
| --- | --- | --- | --- | --- |
| `g01:blueCup01` | `cap:Cup` | `cap:TargetObject` | `cap:Cup` has some `cap:GraspingAffordance` | yes |
| `g01:pinkCup01` | `cap:Cup` | `cap:ReferenceObject` | `cap:Cup` has some `cap:GraspingAffordance` | yes |
| `g01:knife01` | `cap:Knife` | `cap:TargetObject` | `cap:Knife` has some `cap:GraspingAffordance` | yes |
| `g01:fork01` | `cap:Fork` | `cap:TargetObject` | `cap:Fork` has some `cap:GraspingAffordance` | yes |
| `g01:plate01` | `cap:Plate` | `cap:ReferenceObject` | `cap:Plate` has support affordance, not grasping | no |
| `g01:block01` | `cap:ToyBlock` | `cap:CollectableObject` | `cap:ToyBlock` has some `cap:GraspingAffordance` | yes |
| `g01:block02` | `cap:ToyBlock` | `cap:CollectableObject` | `cap:ToyBlock` has some `cap:GraspingAffordance` | yes |
| `g01:basket01` | `cap:Basket` | `cap:ContainerTarget` | `cap:Basket` has containment affordance, not grasping | no |

## Reasoning Workflow

The ontology defines the homework reasoning target:

```ttl
cap:GraspableObject owl:equivalentClass [
    owl:intersectionOf (
        cap:PhysicalObject
        [ owl:onProperty cap:hasAffordance ;
          owl:someValuesFrom cap:GraspingAffordance ]
    )
] .
```

The script `src/reason_and_query.py` loads the course imports and the group ontology, identifies object classes whose OWL restrictions include `cap:hasAffordance some cap:GraspingAffordance`, and materializes inferred `cap:GraspableObject` memberships for instances of those classes. This is a small rule-based reasoning layer over RDFLib, documented here instead of being presented as a complete OWL 2 DL reasoner.

## Running the Workflow

Install the Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

Run reasoning and query generation:

```bash
python3 src/reason_and_query.py
```

This regenerates:

- `ontology/inferred-results.ttl`
- `results/graspable_objects_output.txt`

The repository also includes `results/screenshots/query_output_terminal.png` as a visual record of the command-line query result.

## Query

The required SPARQL query is `queries/graspable_objects.rq`. It retrieves objects typed as `cap:GraspableObject` from the inferred graph.

Expected graspable objects:

- `g01:blueCup01`
- `g01:pinkCup01`
- `g01:knife01`
- `g01:fork01`
- `g01:block01`
- `g01:block02`

`g01:plate01` and `g01:basket01` are intentionally not inferred as graspable because this model treats them as a support/reference object and a container target, respectively.

## Screenshot

The main reproducible workflow was verified through a command-line RDFLib script. The saved text output is the primary reproducible result, and a visual screenshot-style record is included at `results/screenshots/query_output_terminal.png`.

## Widoco and Visual Validation Notes

Widoco was used as an ontology documentation and metadata-quality check for `ontology/group-ontology.ttl`. The documentation was generated with:

```bash
java -jar /private/tmp/widoco-1.4.25.jar \
  -ontFile ontology/group-ontology.ttl \
  -outFolder results/widoco \
  -rewriteAll \
  -webVowl
```

The generated Widoco documentation is available at `results/widoco/doc/index-en.html`, and the WebVOWL visualization is available at `results/widoco/doc/webvowl/index.html`. Widoco successfully parsed the group ontology and generated documentation for the ontology metadata, namespace declaration, classes, properties, individuals, and annotations. This supports the README/report claim that the ontology includes human-readable labels, explanatory comments, ontology metadata, and a clear group namespace.

As an additional visual check, `results/screenshots/ontology_visualization_check.png` was generated from `ontology/inferred-results.ttl`. The visualization confirms that the task objects are connected to their manipulation-task contexts and that the materialized `cap:GraspableObject` instances are `g01:blueCup01`, `g01:pinkCup01`, `g01:knife01`, `g01:fork01`, `g01:block01`, and `g01:block02`. The objects `g01:plate01` and `g01:basket01` are intentionally excluded from `cap:GraspableObject` in this model.

Protege was also used as a desktop visual validation tool. The screenshot `widoco_portege/p.png` shows `ontology/inferred-results.ttl` opened in Protege, with the six expected individuals listed under `physical object > graspable object`.

## Relation to the Final Project

The final project uses a learned robotic manipulation policy to perform the cup-stacking task. The policy receives perception outputs and predicts robot actions for moving a blue cup onto a pink cup. While the learned model handles the physical manipulation process, it does not explicitly represent semantic knowledge about the objects involved in the task.

The ontology-based semantic grounding layer complements the learned policy by providing structured knowledge about object identities, task roles, and affordances. For example, the ontology explicitly represents that `g01:blueCup01` is the target object and `g01:pinkCup01` is the stacking reference object. Through affordance-based reasoning, both objects are inferred to be instances of `cap:GraspableObject`, making their manipulation semantics explicit and queryable.

A robotic system could use this semantic layer before or during task execution. Perception outputs such as object labels and pose frames can be linked to ontology individuals, allowing higher-level reasoning about which objects are relevant to a task. SPARQL queries can then retrieve task-specific information, such as identifying graspable objects or determining which object should be manipulated and which object should serve as the placement target.

Although the current project uses the ontology primarily for semantic grounding and explanation, the same framework could be extended in future work to support task planning, object selection, error recovery, and multi-step manipulation workflows. In this way, the ontology serves as an interpretable knowledge layer that complements the learned policy and provides a semantic bridge between perception and robotic action.
