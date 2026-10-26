"""task_orchestrator_node: ejecuta el arbol de comportamiento de la prueba 5.1.

Contrato (equipo HRI): ver docs/arquitectura.md y docs/contratos_externos.md.
    Publica      /hri/mode, /hri/world_context (modo "libre", despues)
    Ofrece       /hri/skill_request (modo "libre", despues)
    Usa          /hri/converse, /hri/remember, /hri/play_sound y las interfaces
                 de Vision, Navegacion, Brazo y Base (por ahora, stubs)

Uso:
    ros2 run hri_orchestrator task_orchestrator_node
    El arbol se imprime en la terminal en cada tick.
"""
import os

from ament_index_python.packages import get_package_share_directory
import py_trees
import py_trees_ros
import rclpy

from hri_orchestrator.tree.root import create_root

TICK_PERIOD_MS = 500.0      # medio segundo: suficiente para ver el arbol en la terminal
DOORBELL_TIMEOUT_S = 30.0


def main(args=None):
    rclpy.init(args=args)

    places_file = os.path.join(
        get_package_share_directory('hri_orchestrator'), 'config', 'places.yaml')
    root = create_root(places_file=places_file, doorbell_timeout_s=DOORBELL_TIMEOUT_S)
    tree = py_trees_ros.trees.BehaviourTree(root=root, unicode_tree_debug=True)

    try:
        tree.setup(node_name='task_orchestrator_node', timeout=15.0)
    except py_trees_ros.exceptions.TimedOutError as e:
        print(f'No se pudo preparar el arbol: {e}')
        tree.shutdown()
        rclpy.try_shutdown()
        return
    except KeyboardInterrupt:
        tree.shutdown()
        rclpy.try_shutdown()
        return

    tree.tick_tock(period_ms=TICK_PERIOD_MS)

    try:
        rclpy.spin(tree.node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        tree.shutdown()
        rclpy.try_shutdown()


if __name__ == '__main__':
    py_trees.logging.level = py_trees.logging.Level.INFO
    main()
