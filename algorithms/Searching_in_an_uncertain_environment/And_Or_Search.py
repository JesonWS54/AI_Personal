def and_or_search(start_state, goal_state, get_possible_actions, get_action_results):
    """
    Triển khai thuật toán And-Or Search cho môi trường không xác định.

    Trả về: kế hoạch hành động (plan) dạng cây hoặc None nếu không có lời giải.
    """
    def or_search(state, path):
        if state == goal_state:
            return "GOAL"
        if state in path:
            return None  # tránh vòng lặp

        for action in get_possible_actions(state):
            result_states = get_action_results(state, action)
            if not result_states:
                continue
            subplans = and_search(result_states, path + [state])
            if subplans is not None:
                return {"IF": state, "DO": action, "THEN": subplans}

        return None

    def and_search(states, path):
        plan = {}
        for s in states:
            if s in path:
                return None
            subplan = or_search(s, path)
            if subplan is None:
                return None
            plan[s] = subplan
        return plan

    return or_search(start_state, [])
