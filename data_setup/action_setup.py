from controllers.action_controller import get_action_plans


def get_action_plan_id(collection_exercise_id):
    action_plans = get_action_plans()
    for plan in action_plans:
        if _plan_for_collection_exercise(plan, collection_exercise_id):
            return plan['id']
    assert False, f'No Action Plan ID found for collection_exercise_id: {collection_exercise_id}'


def _plan_for_collection_exercise(plan, collection_exercise_id):
    if not plan['selectors']:
        return False
    return plan['selectors']['collectionExerciseId'] == collection_exercise_id
