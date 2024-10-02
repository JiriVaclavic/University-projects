#include "search-strategies.h"
#include "memusage.h"
#include <algorithm>
#include <queue>
#include <stack>

std::vector<SearchAction> BreadthFirstSearch::solve(const SearchState &init_state) {
    std::vector<SearchAction> solution;
    SearchState working_state(init_state);

    auto mem_threshold = mem_limit_ - 10000000;

    if (working_state.isFinal())
        return {};

    auto working_state_sp = std::make_shared<SearchState>(working_state);

    std::queue<std::shared_ptr<SearchState>> open;
    auto map_compare = [](const std::shared_ptr<SearchState>& a, const std::shared_ptr<SearchState>& b) { return *a < *b; };
    std::map<std::shared_ptr<SearchState>, std::pair<std::shared_ptr<SearchState>, SearchAction>, decltype(map_compare)> 
        open_map(map_compare), closed_map(map_compare);

    open.push(std::make_shared<SearchState>(working_state));
    open_map.insert(std::pair<std::shared_ptr<SearchState>, std::pair<std::shared_ptr<SearchState>,
            SearchAction>>(working_state_sp, std::make_pair(nullptr, SearchAction(Location(), Location()))));

    while (!open.empty()) {
        if (getCurrentRSS() > mem_threshold)
            return {};

        auto current_state = open.front();
        open.pop();

        auto state_data_open = open_map.find(current_state);
        decltype(state_data_open) state_data_closed;
        if (state_data_open != open_map.end()) {
            state_data_closed = closed_map.insert(std::pair<std::shared_ptr<SearchState>,
                    std::pair<std::shared_ptr<SearchState>, SearchAction>>(*state_data_open)).first;
            open_map.erase(state_data_open);
        }

        auto actions = current_state->actions();
        for(auto a : actions) {
            SearchState sub_state = a.execute(*current_state);
            if (sub_state.isFinal()) {
                solution.push_back(a);
                while (state_data_closed->second.first){
                    solution.push_back(state_data_closed->second.second);
                    state_data_closed = closed_map.find(state_data_closed->second.first);
                }
                std::reverse(solution.begin(), solution.end());
                return solution;
            }

            auto sp_sub_state = std::make_shared<SearchState>(sub_state);

            if (!(open_map.count(sp_sub_state) || closed_map.count(sp_sub_state))) {
                std::pair map_el = std::make_pair(current_state, a);
                auto r = open_map.insert(std::pair<std::shared_ptr<SearchState>,
                        std::pair<std::shared_ptr<SearchState>, SearchAction>>(sp_sub_state, map_el));
                if (r.second)
                    open.push(sp_sub_state);
            }
        }

    }

    return {};
}

std::vector<SearchAction> DepthFirstSearch::solve(const SearchState &init_state) {
    std::vector<SearchAction> solution;
    SearchState working_state(init_state);
    auto working_state_sp = std::make_shared<SearchState>(working_state);

    auto mem_threshold = mem_limit_ - 10000000;

    if (working_state.isFinal())
        return {};

    std::stack<std::shared_ptr<SearchState>> open;

    auto map_compare = [](const std::shared_ptr<SearchState>& a,
            const std::shared_ptr<SearchState>& b) { return *a < *b; };
    std::map<std::shared_ptr<SearchState>, std::tuple<std::shared_ptr<SearchState>, SearchAction, int>, decltype(
            map_compare)> open_map(map_compare), closed_map(map_compare);

    open.push(std::make_shared<SearchState>(working_state));
    open_map.insert(std::pair<std::shared_ptr<SearchState>, std::tuple<std::shared_ptr<SearchState>, SearchAction,
                    int>>(working_state_sp, std::make_tuple(nullptr, SearchAction(Location(), Location()), 0)));

    while (!open.empty()) {
        if (getCurrentRSS() > mem_threshold)
            return {};

        auto current_state = open.top();
        open.pop();

        auto state_data_open = open_map.find(current_state);
        decltype(state_data_open) state_data_closed;
        if (state_data_open != open_map.end()) {
            state_data_closed = closed_map.insert(std::pair<std::shared_ptr<SearchState>,
                    std::tuple<std::shared_ptr<SearchState>, SearchAction, int>>(*state_data_open)).first;
            open_map.erase(state_data_open);
        }

        if (std::get<2>(state_data_closed->second) >= depth_limit_) {
            continue;
        }

        auto actions = current_state->actions();
        for(auto a : actions) {
            SearchState sub_state = a.execute(*current_state);
            if (sub_state.isFinal()) {
                solution.push_back(a);
                while (std::get<0>(state_data_closed->second)){
                    solution.push_back(std::get<1>(state_data_closed->second));
                    state_data_closed = closed_map.find(std::get<0>(state_data_closed->second));
                }
                std::reverse(solution.begin(), solution.end());
                return solution;
            }

            int new_level = std::get<2>(state_data_closed->second) + 1;
            if (new_level < depth_limit_) {
                auto sp_sub_state = std::make_shared<SearchState>(sub_state);

                if (!(open_map.count(sp_sub_state) || closed_map.count(sp_sub_state))) {
                    std::tuple map_el = std::make_tuple(current_state, a, new_level);
                    auto r = open_map.insert(std::pair<std::shared_ptr<SearchState>,
                            std::tuple<std::shared_ptr<SearchState>, SearchAction, int>>(sp_sub_state, map_el));
                    if (r.second)
                        open.push(sp_sub_state);
                }
            }
        }

    }

    return {};
}

double StudentHeuristic::distanceLowerBound(const GameState &state) const {
    int nb_not_home = king_value * colors_list.size();
    for (const auto &home : state.homes) {
        auto opt_top = home.topCard();
        if (opt_top.has_value())
            nb_not_home -= opt_top->value;
    }

    int nb_fc_used = 0;
    for (const auto &free_cell : state.free_cells) {
        auto opt_top = free_cell.topCard();
        if (opt_top.has_value())
            nb_fc_used++;
    }

    int nb_bigger_on_smaller = 0;
    for (const auto &stack : state.stacks) {
        auto cards = stack.storage();
        for (size_t i = 1; i < stack.nbCards(); i++) {
            if (cards[i].value > cards[i - 1].value)
                nb_bigger_on_smaller += (stack.nbCards() - i);
        }
    }
    return 1.2 * (0.7 * nb_not_home + 0.2 * nb_bigger_on_smaller + 0.1 * nb_fc_used);
}

std::vector<SearchAction> AStarSearch::solve(const SearchState &init_state) {
    std::vector<SearchAction> solution;
    SearchState working_state(init_state);
    auto working_state_sp = std::make_shared<SearchState>(working_state);

    auto mem_threshold = mem_limit_ - 10000000;

    if (working_state.isFinal())
        return {};

    auto pq_compare = [](auto a, auto&& b)
    { return (b.second.second + b.second.first) < (a.second.second + a.second.first); };
    std::priority_queue<std::pair<std::shared_ptr<SearchState>, std::pair<int, double>>,
            std::vector<std::pair<std::shared_ptr<SearchState>, std::pair<int, double>>>, decltype(pq_compare)>
            open(pq_compare);

    auto map_compare = [](const std::shared_ptr<SearchState>& a,
            const std::shared_ptr<SearchState>& b) { return *a < *b; };
    std::map<std::shared_ptr<SearchState>, std::pair<std::shared_ptr<SearchState>, SearchAction>, decltype(
            map_compare)> open_map(map_compare), closed_map(map_compare);

    open.push(std::make_pair(std::make_shared<SearchState>(working_state),
                             std::make_pair(0, compute_heuristic(working_state, *heuristic_))));
    open_map.insert(std::pair<std::shared_ptr<SearchState>, std::pair<std::shared_ptr<SearchState>, SearchAction>>(
            working_state_sp, std::make_pair(nullptr, SearchAction(Location(), Location()))));

    while (!open.empty()) {
        if (getCurrentRSS() > mem_threshold) {
            return {};
        }

        auto cs_data = open.top();
        auto current_state = cs_data.first;
        open.pop();

        auto state_data_open = open_map.find(current_state);
        decltype(state_data_open) state_data_closed;
        if (state_data_open != open_map.end()) {
            state_data_closed = closed_map.insert(std::pair<std::shared_ptr<SearchState>,
                    std::pair<std::shared_ptr<SearchState>, SearchAction>>(*state_data_open)).first;
            open_map.erase(state_data_open);
        }

        auto actions = current_state->actions();

        for(auto a : actions) {
            SearchState sub_state = a.execute(*current_state);
            if (sub_state.isFinal()) {
                solution.push_back(a);
                while (state_data_closed->second.first){
                    solution.push_back(state_data_closed->second.second);
                    state_data_closed = closed_map.find(state_data_closed->second.first);
                }
                std::reverse(solution.begin(), solution.end());
                return solution;
            }

            auto sp_sub_state = std::make_shared<SearchState>(sub_state);

            if (!(open_map.count(sp_sub_state) || closed_map.count(sp_sub_state))) {
                int new_level = cs_data.second.first;
                auto map_el = std::make_pair(current_state, a);
                auto queue_el = std::make_pair(
                        sp_sub_state, std::make_pair(
                                new_level + 1, compute_heuristic(sub_state, *heuristic_)));
                auto r = open_map.insert(std::pair<std::shared_ptr<SearchState>,
                        std::pair<std::shared_ptr<SearchState>, SearchAction>>(sp_sub_state, map_el));
                if (r.second)
                    open.push(queue_el);
            }
        }
    }
    return {};
}
