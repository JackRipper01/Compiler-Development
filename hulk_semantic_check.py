# region temp import 
from hulk_parser import hulk_parse
from misc import set_depth, LCA, create_Hierarchy_graph, trasspass_params_to_children
# endregion

import visitor

from hulk_ast import (
    Node, #NAN
    Program,
    FunctionDef,
    FunctionCall,
    Params,
    ExpressionBlock,
    Let,
    Assign,
    ID,
    If,
    Case,
    While,
    For, #NAN
    TrueLiteral, #NAN
    FalseLiteral, #NAN
    TypeDef,
    TypeCall,
    Protocol,
    VectorExt,
    VectorInt,
    VectorCall,
    BinOp,
    UnaryOp,
    Num, #NAN
    StringLiteral, #NAN
    Pi, #NAN
    E, #NAN
    Print,
    Sqrt,
    Sin,
    Cos,
    Exp,
    Log,
    Rand, #NAN
)

class HierarchyNode:
    def __init__(self, name, parent, children, depth):
        self.name = name
        self.parent = parent
        self.children = children
        self.depth = depth
        

class ScopeBuilder:
    def __init__(self):
        self.errors = []
        self.inside_types = False # desarrollar idea

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node: Program):
        if node.global_exp:
            node.global_exp.variable_scope = node.variable_scope
            self.visit(node.global_exp)
        else:
            self.errors.append("Global Expression required")
        
    @visitor.when(Print)
    def visit(self, node: Print):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
        
    @visitor.when(Sqrt)
    def visit(self, node: Sqrt):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
        
    @visitor.when(Sin)
    def visit(self, node: Sin):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
        
    @visitor.when(Cos)
    def visit(self, node: Cos):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
        
    @visitor.when(Exp)
    def visit(self, node: Exp):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
        
    @visitor.when(Log)
    def visit(self, node: Log):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
    
    @visitor.when(ID)
    def visit(self, node: ID):
        if node.name not in node.variable_scope:
            self.errors.append("Variable "+node.name+" not defined")
    
    @visitor.when(Params)
    def visit(self, node: Params):
        for param in node.param_list:
            param.variable_scope = node.variable_scope
            self.visit(param)
    
    @visitor.when(BinOp)
    def visit(self, node: BinOp):
        node.left.variable_scope = node.variable_scope
        self.visit(node.left)
        if node.op != ".":
            node.right.variable_scope = node.variable_scope
            self.visit(node.right)
        else:
            if type(node.right) is FunctionCall:
                node.right.params.variable_scope = node.variable_scope
                self.visit(node.right.params)
                # check context from class
        
    @visitor.when(UnaryOp)
    def visit(self, node: UnaryOp):
        node.operand.variable_scope = node.variable_scope
        self.visit(node.operand)
        
    @visitor.when(FunctionCall)
    def visit(self, node: FunctionCall):
        fn_name = node.func_id.name+"/"+str(len(node.params.param_list))
        if fn_name not in node.global_definitions:
            print(node.global_definitions)
            self.errors.append("Function "+fn_name+" not defined")
        node.params.variable_scope = node.variable_scope
        self.visit(node.params)
    
    @visitor.when(TypeCall)
    def visit(self, node: TypeCall):
        if node.id.name in node.global_definitions:
            if len(node.params.param_list) != len(node.global_definitions[node.id.name].params.param_list):
                self.errors.append("Amount of params doesnt match type definition of "+node.id.name+" ("+str(len(node.global_definitions[node.id.name].params.param_list))+") and its instanstiation ("+str(len(node.params.param_list))+")")
            node.params.variable_scope = node.variable_scope
            self.visit(node.params)
        else:
            self.errors.append("Type "+ node.id.name+" not defined")
    
    @visitor.when(ExpressionBlock)
    def visit(self, node: ExpressionBlock):
        for exp in node.exp_list:
            exp.variable_scope = node.variable_scope
            self.visit(exp)
            
    @visitor.when(Assign)
    def visit(self, node: Assign):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)
        
    @visitor.when(If)
    def visit(self, node: If):
        for case_item in node.case_list:
            case_item.variable_scope = node.variable_scope
            self.visit(case_item)
            
    @visitor.when(While)
    def visit(self, node: While):
        node.condition.variable_scope = node.variable_scope
        self.visit(node.condition)
        node.body.variable_scope = node.variable_scope
        self.visit(node.body)
    
    @visitor.when(Case)
    def visit(self, node: Case):
        node.condition.variable_scope = node.variable_scope
        self.visit(node.condition)
        node.body.variable_scope = node.variable_scope
        self.visit(node.body)
        
        
    @visitor.when(Let)
    def visit(self, node: Let):
        node.assign[0].variable_scope = node.variable_scope
        self.visit(node.assign[0])
        node.variable_scope = node.variable_scope.copy()
        node.variable_scope[node.assign[0].name.name] = (node.assign[0].name, node.assign[0].value)
        node.body.variable_scope = node.variable_scope
        self.visit(node.body)
    
    def get_global_definitions(self, ast_input : Program):
        ast_input.global_definitions["Number"] = "float"
        ast_input.global_definitions["String"] = "string"
        ast_input.global_definitions["Boolean"] = "int"
        
        for function in ast_input.functions:
            function_name = function.func_id.name+"/"+str(len(function.params.param_list))
            if function_name in ast_input.global_definitions:
                self.errors.append("Function "+ function_name +" already defined: ")
            else:
                ast_input.global_definitions[function_name] = function
        
        for type_def in list(ast_input.types)+list(ast_input.protocols):
            type_name = type_def.id.name
            if type_name in ast_input.global_definitions:
                self.errors.append("Type "+ type_name+" already defined: ")
            else:
                ast_input.global_definitions[type_name] = type_def
    
    def hierarchy_tree_build(self, ast_root: Program):
        hierarchy_tree = {}
        hierarchy_tree["Object"] = HierarchyNode("Object", None, [], 0)
        hierarchy_tree["Number"] = HierarchyNode("Number","Object",[],1)
        hierarchy_tree["String"] = HierarchyNode("String","Object",[],1)
        hierarchy_tree["Boolean"] = HierarchyNode("Boolean","Object",[],1)
        hierarchy_tree["Object"].children.append("Number")
        hierarchy_tree["Object"].children.append("String")
        hierarchy_tree["Object"].children.append("Boolean")
        
        for type_name in ast_root.types: 
            hierarchy_tree[type_name.id.name] = HierarchyNode(type_name.id.name, None, [], 0)
            
        for type_name in ast_root.types:
            current_type = type_name.id.name
            
            if type_name.inherits:
                inherits_from = type_name.inherits.id.name
                if type(ast_root.global_definitions[inherits_from]) is str:
                    self.errors.append("Cannot inherit from type "+inherits_from)
                    continue
                hierarchy_tree[current_type].parent = inherits_from
                hierarchy_tree[inherits_from].children.append(current_type)
            else:
                hierarchy_tree[current_type].parent = "Object"
                hierarchy_tree["Object"].children.append(current_type)
        # print(*[str(x)+str(hierarchy_tree[x].children) for x in hierarchy_tree], sep="\n")
        err = set_depth(hierarchy_tree, "Object", set())
        if err:
            self.errors.append(err)
        return hierarchy_tree

        
    def check_tree(self, i_dict, root):
        qww = [root]
        visited = set()
        while len(qww)>0:
            current = qww.pop(0)
            visited.add(current)
            for child in i_dict[current].children:
                if child in visited:
                    self.errors.append("Error en la definicion del tipo: "+child)
                else:
                    qww.append(child)
        if len(visited) != len(i_dict):
            self.errors.append("Error en la definicion de tipos involucrando a los tipos: "+str(set(i_dict).difference(visited)))
    
    
        
                
def semantic_check(ast: Program):
    scope_visitor = ScopeBuilder()
    scope_visitor.get_global_definitions(ast)
    type_hierarchy_tree = scope_visitor.hierarchy_tree_build(ast)
    scope_visitor.check_tree(type_hierarchy_tree, "Object")
    trasspass_params_to_children(type_hierarchy_tree, "Object",ast)
    scope_visitor.visit(ast)
    # your code here
    print("SEMANTIC CHECK FOUND THE FOLLOWING ERRORS:" if len(scope_visitor.errors)>0 else "SUCCESS PERFORMING SEMANTIC CHECKING!!!",*scope_visitor.errors, sep="\n")


if __name__ == "__main__":
    ast,_ = hulk_parse(r"""type Animal(a){}
                               type Felino inherits Animal{}
                               type Gato inherits Felino {}
                               type Canino inherits Animal{}
                               type Perro inherits Canino {}
                               type Lobo inherits Canino{}
                               function asd(a,b,c) => print(a);
                               let a = 5, b = a in {print(new Lobo(2,2));}""")
    if (ast):
        semantic_check(ast)
    