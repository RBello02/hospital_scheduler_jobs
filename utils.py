import re
import matplotlib
matplotlib.use("Agg")  # Usa un backend non interattivo
import matplotlib.pyplot as plt
import os
import json 


def preprocess (data, rooms_mapping, patients_mapping, occupants_mapping ,surgeons_mapping, nurses_mapping, theaters_mapping ):
    
    total_days= data['days']
    total_shifts = data['shift_types']
    #skill_levels = data['skill_levels']
    age_groups = data['age_groups']

    age_to_number = {age: i + 1 for i, age in enumerate(age_groups)}   # dic

    shift_to_number = {shift: i for i, shift in enumerate(total_shifts)} 

    shifts = [shift_to_number[shift] for shift in total_shifts]

     # create a dic for occupants

    occupants_data = data['occupants']

    # create a dic for patients

    patients_data = data['patients']

    # create a dic for surgeons

    surgeons_data = data['surgeons']

    # create a dic for operating theaters

    operating_theaters_data = data['operating_theaters']

    # create a dic for the nurses

    nurses_data = data['nurses']

    # create a dic for rooms

    rooms_data = data['rooms']

    rooms_id = [room_data['id'] for room_data in rooms_data]

    # modifying the id to be a list of integers

    for room_data in rooms_data:
         room_data['id'] = rooms_mapping[room_data['id']]   # modifying the id 
    

    for occupant_data in occupants_data:
        occupant_data['id'] = occupants_mapping[occupant_data['id']]   # change the id
        occupant_data['room_id'] = rooms_mapping[occupant_data['room_id']]   # change the id
        if occupant_data['gender'] == 'A':
            occupant_data['gender'] = 0
        else:
            occupant_data['gender'] = 1

        occupant_data['age_group'] = age_to_number.get(occupant_data['age_group'])

    for nurse_data in nurses_data:
        nurse_data['id'] = nurses_mapping[nurse_data['id']]

    for surgeon_data in surgeons_data:
        surgeon_data['id'] = surgeons_mapping[surgeon_data['id']]
    
    for theater_data in operating_theaters_data:
        theater_data['id'] = theaters_mapping[theater_data['id']]

    for patient_data in patients_data:
        patient_data['id'] = patients_mapping[patient_data['id']]   # change the id
        patient_data['surgeon_id'] = surgeons_mapping[patient_data['surgeon_id']]   # change the id
        if patient_data['gender'] == 'A':
            patient_data['gender'] = 0
        else:
            patient_data['gender'] = 1

        if patient_data['mandatory'] == False:
            patient_data['mandatory'] = 0
        else:
            patient_data['mandatory'] = 1

        patient_data['age_group'] = age_to_number.get(patient_data['age_group'])

        patient_data['compatible_rooms_ids'] = [room_id for room_id in rooms_id if room_id not in patient_data['incompatible_room_ids']]
        patient_data['compatible_rooms_ids'] = [rooms_mapping[c_room] for c_room in patient_data['compatible_rooms_ids']]    # creating a feature with compatible rooms

        



    return {'T': total_days,'shifts': shifts ,'age_mapping': age_to_number,'shift_mapping': shift_to_number ,'occupants': occupants_data, 'patients':patients_data, 'surgeons': surgeons_data, 'nurses': nurses_data ,'rooms': rooms_data, 'theaters': operating_theaters_data, 'weights': data['weights'] }



def postprocess (solution, patients, surgeons, nurses, rooms, theaters, T, shifts, shift_mapping, filename , weights, tot_cost=0, cost_dic=0):

    # this function produces the json file for the validation of the solution

    # get the number of patients
    n_patients = len(patients)
    num_digits_for_patient = len(str(n_patients))

    # get the number of theaters
    n_theaters = theaters.n_theaters
    num_digits_for_theater = len(str(n_theaters))

    # get the number of rooms
    n_rooms = rooms.n_rooms
    num_digits_for_room = len(str(n_rooms))

    # starting from the patients
    patients_solution = []

    for patient in patients:
        patient_dic = solution.patient_schedule[patient.id]
        patient_id_str = f"p{patient.id:0{num_digits_for_patient}d}"
        if patient_dic['day'] is None:          # it means that the patient is not in the hospital
            patients_solution.append({"id": patient_id_str,
                                      "admission_day": "none"})
        else:
            # get the operating theater where the patient is
            for operating in solution.surgeons_operations:
                if operating['patient'].id == patient.id:
                    if operating['theater'] is not None:
                       theater_id = operating['theater']   # found the theater
            
            patients_solution.append({"id": patient_id_str,
                                      "admission_day": patient_dic['day'],
                                      "room": f"r{patient_dic['room']:0{num_digits_for_room}d}",
                                      "operating_theater": f"t{theater_id:0{num_digits_for_theater}d}"})
            
    
    # now we go for the nurses

    # get the number of nurses
    n_nurses = len(nurses)
    num_digits_for_nurse = len(str(n_nurses))

    nurses_solution = []

    match = re.search(r'\d+', filename)
    if match:
        test_number = int(match.group())  # it convert the number into integer
    else:
        print("The filename doesn't contain a number")

    for nurse in nurses:
        nurse_assignment= []
        if test_number > 5:
            nurse_id_str = f"n{nurse.id:0{num_digits_for_nurse+1}d}"     # IF THE VALIDATOR DOESN'T WORK ADD +1, WITH SOME TEST THIS COMMAND DOESN'T WORK
        else:
            nurse_id_str = f"n{nurse.id:0{num_digits_for_nurse}d}"     # IF THE VALIDATOR DOESN'T WORK ADD +1, WITH SOME TEST THIS COMMAND DOESN'T WORK
        for day in range(T):
            for shift in shifts:
                if nurse.possible_turns[day][shift] > 0:   # check if the nurse can work on that day
                    rooms_set = set()   # is the set of the rooms where the nurse is working
                    for room_id in rooms.rooms_id:
                        nurse_list = solution.nurses_schedule[day][shift][room_id]   # get the nurses that work in that particular room
                        #print(nurse_list)
                        for nurse_dic in nurse_list:
                            if nurse_dic['nurse'].id == nurse.id:
                                rooms_set.add(f"r{room_id:0{num_digits_for_room}d}")
                    
                    rooms_list = list(rooms_set) # rooms_set becomes a list
                    rooms_list.sort()
                    nurse_assignment.append({"day": day, "shift": next((k for k, v in shift_mapping.items() if v == shift), None), "rooms": rooms_list})
        nurses_solution.append({"id": nurse_id_str, "assignments": nurse_assignment})

    # add the costs

    if not (tot_cost == 0 and cost_dic == 0):
        string_cost = ["Costs: "+str(int(tot_cost))+", Unscheduled: "+str(int(cost_dic['S8']/weights['unscheduled_optional']))+",  Delay: " + str(int(cost_dic['S7']/weights['patient_delay'])) + ",  OpenOT: " + str(int(cost_dic['S5']/weights['open_operating_theater'])) + ",  AgeMix: " + str(int(cost_dic['S1']/weights['room_mixed_age'])) + ",  Skill: " + str(int(cost_dic['S2']/weights['room_nurse_skill'])) + ",  Excess: " + str(int(cost_dic['S4']/weights['nurse_eccessive_workload'])) + ",  Continuity: " + str(int(cost_dic['S3']/weights['continuity_of_care'])) + ",  SurgeonTransfer: " + str(int(cost_dic['S6']/weights['surgeon_transfer']))]
    else:
        string_cost = ""

    # return the json file

    return {"patients": patients_solution, "nurses": nurses_solution, "costs": string_cost}


def ALNS_plot(x_plot,y_plot,filename, destroy_prob_vec = [], repair_prob_vec = [], iter = 1000,  flag = False, Gamma=1, rho=1, Delta=[4,3,2,1], time_destroy=None, time_repair=None):

    plot_folder = "plots"
    file_number = filename.replace('test', '').replace('.json', '')

    solution_folder = "test_data/solutions"
    solution_filename = filename.replace('test', 'sol_test')

    with open(solution_folder+'/'+solution_filename, 'r') as file:
        data = json.load(file)

    cost_string = data["costs"][0]
    match = re.search(r"Cost:\s*(\d+)", cost_string)
    if match:
        real_cost_value = int(match.group(1))

    plt.figure(figsize=(8, 5))
    plt.plot(x_plot, y_plot, label='OBJECTIVE FUNCTION FOR TEST ' +str(file_number)+  ' VS ALNS ITERATIONS, total of '+ str(iter)+ ' iterations', marker='o', linestyle='-',  markersize=0.5)

    if flag:
        plt.axhline(y=real_cost_value, color='r', linestyle='-', label='optimal value')

    plt.xlabel('Iterations')
    plt.ylabel('Objective function value')
    plt.legend()
    plt.grid()

    output_path = os.path.join(plot_folder, f'plot_test{file_number}.png')
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.close()

    if destroy_prob_vec and repair_prob_vec:

        # create a vector for each destroy and repair method
        destroy_methods = [method for method in destroy_prob_vec[0].keys()]
        repair_methods = [method for method in repair_prob_vec[0].keys()]

        destroy_dic = {}
        for method in destroy_methods:
            destroy_dic[method] = []
            for prob in destroy_prob_vec:
                destroy_dic[method].append(prob[method])

        repair_dic = {}
        for method in repair_methods:
            repair_dic[method] = []
            for prob in repair_prob_vec:
                repair_dic[method].append(prob[method])
            
        plt.figure(figsize=(12, 6))
        for label, values in destroy_dic.items():
            plt.plot(values, label=label)

        plt.xlabel('Iterations')
        plt.ylabel('Destroy probability')   
        plt.title('plot of Destroy probabilities for test ' + str(file_number) + ' vs ALNS iterations, total of '+ str(iter)+ ' iterations')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.grid(True)
        plt.tight_layout()

        output_path = os.path.join(plot_folder, f'Destroy_plot_test{file_number}.png')
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

        plt.figure(figsize=(12, 6))
        for label, values in repair_dic.items():
            plt.plot(values, label=label)

        plt.xlabel('Iterations')
        plt.ylabel('Repair probability')   
        plt.title('plot of Repair probabilities for test ' + str(file_number) + ' vs ALNS iterations, total of '+ str(iter)+ ' iterations')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.grid(True)
        plt.tight_layout()

        output_path = os.path.join(plot_folder, f'Repair_plot_test{file_number}.png')
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    text_folder = "text_output"
    with open(f'{text_folder}/test_{file_number}.txt', 'w') as file:

        file.write("\n")
        file.write("ALNS iterations: " + str(iter) + "\n")
        print("\n")
        print("\n")
        file.write("rho: " + str(rho) + "\n")
        file.write("Gamma: " + str(Gamma) + "\n")
        file.write("Delta: " + str(Delta) + "\n")
        print("\n")

        if time_destroy is not None and time_repair is not None:

            file.write("Optimal value found by ALNS: {:.2f}\n".format(min(y_plot)))
            file.write("Real optimal value: {:.2f}\n".format(real_cost_value))
            file.write("\n")
            file.write("Time for optimization: {:.2f}\n".format(time_destroy + time_repair))
            file.write("Time for destroy: {:.2f}, {:.2f}% of the total time\n".format(time_destroy, 100 * time_destroy / (time_destroy + time_repair)))
            file.write("Time for repair: {:.2f}, {:.2f}% of the total time\n".format(time_repair, 100 * time_repair / (time_destroy + time_repair)))

    file.close()  


    return 0




