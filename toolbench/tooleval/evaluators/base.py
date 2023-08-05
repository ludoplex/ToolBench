import random
from typing import List, Union, Dict, Any, Callable
from .utils import register_evaluator

def process_answer(answer: Dict):
    answer['final_answer'] = answer['final_answer'][:1000]
    answer['answer_details'] = answer['answer_details'][:3000]
    answer.pop('method', None)
    return answer


def process_tools(tools: List[Dict]):
    for tool in tools:
        tool.pop('description', None)
        tool.pop('parameters', None)
    return tools

@register_evaluator
class BaseEvaluator:
    """Base class for evaluators.
    
    Attributes:
    ----------
        fn_completions : Callable[[Dict,List[Dict]],int]
            The completion function of the evaluator, used to get annotated results.
            This function should take two arguments: `task_description`:Dict and `answers`:List[Dict], return a int stand for the index of best answer.
    
    Functions:
    ---------
        annotate_preference : Callable
            Annotate and return the index of the preferred answer.
        
    """
    def __init__(self,
                 fn_completions: Callable[[Dict,List[Dict]],int] = None,
                 *args,
                 **kwargs):
        self.fn_completions = fn_completions

    def annotate_preference(self,
                            query: str,
                            available_tools: List[Dict[Any, Any]],
                            ans1: Dict, ans2: Dict,
                            multisample=False,
                            sample_n=4) -> Union[List[int], int]:
        """Annotate and return the index of the preferred answer.
        
        For given query, available tools, and two answers, return the index of the preferred answer by calling function `fn_completions` of the evaluator.
        
        Parameters:
        ----------
        
        Returns:
        -------
        
        Raise:
        -----
        
        """
        ans1, ans2 = process_answer(ans1), process_answer(ans2)
        available_tools = process_tools(available_tools)
        if not multisample:
            return (
                self.fn_completions(
                    {'query': query, 'available_tools': available_tools},
                    [ans1, ans2],
                )
                if random.random() < 0.5
                else 1
                - self.fn_completions(
                    {'query': query, 'available_tools': available_tools},
                    [ans2, ans1],
                )
            )
        prefers = []
        for _ in range(sample_n):
            if random.random() < 0.5:
                prefers.append(self.fn_completions(
                    {'query': query, 'available_tools': available_tools}, [ans1, ans2]))
            else:
                prefers.append(1 - self.fn_completions(
                    {'query': query, 'available_tools': available_tools}, [ans2, ans1]))
        return prefers

