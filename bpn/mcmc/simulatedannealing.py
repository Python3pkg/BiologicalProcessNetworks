#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011 Chris D. Lasher & Phillip Whisenhunt
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""Simulated Annealing for BPN."""


import math
import random
import states

import logging
logger = logging.getLogger('bpn.sabpn.simulatedannealing')

from defaults import NUM_STEPS


class SimulatedAnnealing(object):
    pass


class PLNSimulatedAnnealing(SimulatedAnnealing):
    """A class representing Simulated Annealing for process linkage
    networks.

    """
    def __init__(
            self,
            annotated_interactions,
            active_gene_threshold,
            transition_ratio,
            num_steps=NUM_STEPS,
            selected_links=None,
            alpha=None,
            beta=None,
            link_prior=None,
            parameters_state_class=states.PLNParametersState
        ):
        """Create a new instance.

        :Parameters:
        - `annotated_interactions`: an `AnnotatedInteractionsGraph`
          instance
        - `active_gene_threshold`: the threshold at or above which a
          gene is considered "active"
        - `transition_ratio`: a `float` indicating the ratio of link
          transitions to parameter transitions
        - `num_steps`: the number of steps to take anneal
        - `selected_links`: a user-defined seed of links to start as
          selected
        - `alpha`: the false-positive rate; see `PLNParametersState` for
          more information
        - `beta`: the false-negative rate; see `PLNParametersState` for
          more information
        - `link_prior`: the assumed probability we would pick any one
          link as being active; see `PLNParametersState` for more
          information
        - `state_recorder_class`: the class of the state recorder to use
          [default: `recorders.PLNStateRecorder`]
        - `parameters_state_class`: the class of the parameters state to
          use [default: `states.PLNParametersState]`

        """
        self.current_state = states.PLNOverallState(
                annotated_interactions,
                active_gene_threshold,
                transition_ratio,
                selected_links,
                alpha,
                beta,
                link_prior,
                parameters_state_class

        )
        self.state_recorder = state_recorder_class(
                self.current_state.links_state.process_links,
                self.current_state.parameters_state.get_parameter_distributions()
        )
        self.num_steps = num_steps
        self.temperature = 1.0
        self.step_size = (1.0/self.num_steps)


    def next_state(self):
        """Move to the next state in Simulated Annealing.

        This method creates a proposed state for a transition; it then
        assesses the "fitness" of this new state by comparing the
        likelihood of the proposed state to the likelihood of the
        current state as a (log of the) ratio of the two likelihoods.

        If this ratio is greater than 0 or the current temperature is
		greater then a random value from 0 to 1, then we accept the 
		proposed state and transition to it. Otherwise we reject the 
		proposed state and continue with the current state.

        """
        proposed_state = self.current_state.create_new_state()
        proposed_transition_type = proposed_state._delta[0]
        current_log_likelihood = \
                self.current_state.calc_log_likelihood()
        proposed_log_likelihood = \
                proposed_state.calc_log_likelihood()
        delta_e_log = proposed_log_likelihood - \
                current_log_likelihood

        # Is the new solution better?
        if delta_e_log > 0 or self.temperature > random.random():
            print "Accepted new state"
            self.current_state = proposed_state
            logger.debug("Accepted proposed state.")
            log_state_likelihood = proposed_log_likelihood
        else:
            print "Reject Random state"
            logger.debug("Rejected proposed state.")
            log_state_likelihood = current_log_likelihood

        logger.debug("Log of state likelihood: %s" % (
                log_state_likelihood))


    def run(self):
        """Anneal for num_steps.

        """
        while self.temperature > 0:
            self.next_state()
            self.temperature -= self.step_size

class ArraySimulatedAnnealing(PLNSimulatedAnnealing):
    """Similar to `PLNSimulatedAnnealing`, but using `numpy` 
	arrays to track state information.

    """
    def __init__(
            self,
            annotated_interactions,
            active_gene_threshold,
            transition_ratio,
            num_steps=NUM_STEPS,
            selected_links_indices=None,
            alpha=None,
            beta=None,
            link_prior=None,
            parameters_state_class=states.PLNParametersState,
            links_state_class=states.ArrayLinksState
        ):
        """Create a new instance.

        :Parameters:
        - `annotated_interactions`: an `AnnotatedInteractionsArray`
          instance
        - `active_gene_threshold`: the threshold at or above which a
          gene is considered "active"
        - `transition_ratio`: a `float` indicating the ratio of link
          transitions to parameter transitions
        - `num_steps`: the number of steps to anneal
        - `selected_links_indices`: a user-defined seed of indices to
          links to start as selected
        - `alpha`: the false-positive rate; see `PLNParametersState` for
          more information
        - `beta`: the false-negative rate; see `PLNParametersState` for
          more information
        - `link_prior`: the assumed probability we would pick any one
          link as being active; see `PLNParametersState` for more
          information
        - `state_recorder_class`: the class of the state recorder to use
          [default: `recorders.ArrayStateRecorder`]
        - `parameters_state_class`: the class of the parameters state to
          use [default: `states.PLNParametersState`]
        - `links_state_class`: the class of the links state to use
          [default: `states.ArrayLinksState`]

        """
        self.current_state = states.ArrayOverallState(
                annotated_interactions,
                active_gene_threshold,
                transition_ratio,
                selected_links_indices,
                alpha,
                beta,
                link_prior,
                parameters_state_class,
                links_state_class
        )
        self.num_steps = num_steps
        self.last_transition_info = None
        self.temperature = 1.0
        self.step_size = 1.0/self.num_steps