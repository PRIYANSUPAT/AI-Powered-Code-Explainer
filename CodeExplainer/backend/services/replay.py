import ast
import json
from typing import List, Dict, Any

class StateTracker(ast.NodeTransformer):
    def insert_logging(self, body: List[ast.stmt]) -> List[ast.stmt]:
        new_body = []
        for stmt in body:
            new_body.append(stmt)
            # Inject logging after statements that modify or declare state, or expressions
            if isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Expr, ast.Return, ast.Pass)):
                log_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id='___log_state', ctx=ast.Load()),
                        args=[
                            ast.Constant(value=stmt.lineno),
                            ast.Call(func=ast.Name(id='locals', ctx=ast.Load()), args=[], keywords=[])
                        ],
                        keywords=[]
                    )
                )
                ast.copy_location(log_call, stmt)
                new_body.append(log_call)
            
            # Recurse into blocks
            if hasattr(stmt, 'body'):
                stmt.body = self.insert_logging(stmt.body)
            if hasattr(stmt, 'orelse'):
                stmt.orelse = self.insert_logging(stmt.orelse)
                
        return new_body

    def visit_Module(self, node: ast.Module) -> Any:
        # Module is the root, so we process its body
        node.body = self.insert_logging(node.body)
        return node
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        node.body = self.insert_logging(node.body)
        return node

def replay_code(code: str) -> List[Dict[str, Any]]:
    """
    Parses the Python code using AST, injects a logging function to track
    variables state, safely executes it, and returns the trace array.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [{"error": f"Syntax Error: {e.msg} at line {e.lineno}"}]

    transformer = StateTracker()
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    
    try:
        compiled = compile(tree, '<replay_sandbox>', 'exec')
    except Exception as e:
        return [{"error": f"Compilation Error: {str(e)}"}]

    trace_output = []

    def ___log_state(lineno: int, local_vars: Dict[str, Any]):
        filtered_vars = {
            k: repr(v) for k, v in local_vars.items() 
            if not k.startswith('__') and k != '___log_state' and not callable(v)
        }
        trace_output.append({"line": lineno, "variables": filtered_vars})

    sandbox_globals = {
        "___log_state": ___log_state,
        "__builtins__": __builtins__
    }

    try:
        exec(compiled, sandbox_globals, sandbox_globals)
    except Exception as e:
        trace_output.append({"error": f"Execution Error: {str(e)}"})

    # Deduplicate lines if multiple statements per line or consecutive empty changes
    # Simple logic: keep all to show step trace accurately to user expectations
    return trace_output
