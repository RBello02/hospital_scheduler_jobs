

def visual_schedule(solution, occupants,  rooms, T, flag = False):

    if not flag:
        for t in range(T):
            print(f"************Day {t}*************")
            for room_id in rooms.rooms_id:
                print(f"room {room_id} RGender {rooms.rooms_gender[t][room_id]} RCounter {rooms.rooms_count_people[t][room_id]} RCapacity {rooms.rooms_capacity[room_id]}, [ ", end = " ")
                capacity = rooms.rooms_capacity[room_id]
                counter = 0
                for schedule in solution.patient_schedule:
                    patient = schedule['patient']
                    start = schedule['day']
                    room_of_patient = schedule['room']
                    if room_id == room_of_patient and start is not None:
                        end = start + patient.length_of_stay
                        if start <= t < end:
                            print(f" PID {patient.id}|PG {patient.gender} ", end = " ")
                            counter += 1
                for occupant in occupants:
                    if occupant.room_id == room_id and t < occupant.length_of_stay:
                        print(f" OID {occupant.id}|OG {occupant.gender} ", end = " ")
                        counter += 1
                for i in range(counter, capacity):
                    print(" __ ", end=" ")
                print(" ] ")

    else:

        print(r'''
       ,
       \`-._           __
        \\  `-..____,.'  `.
         :`.         /    \`.
         :  )       :      : \
          ;'        '   ;  |  :
          )..      .. .:.`.;  :
         /::...  .:::...   ` ;
         ; _ '    __        /:\
         `:o>   /\o_>      ;:. `.
        `-`.__ ;   __..--- /:.   \
        === \_/   ;=====_.':.     ;
         ,/'`--'...`--....        ;
              ;                    ;
            .'                      ;
          .'                        ;
        .'     ..     ,      .       ;
       :       ::..  /      ;::.     |
      /      `.;::.  |       ;:..    ;
     :         |:.   :       ;:.    ;
     :         ::     ;:..   |.    ;
      :       :;      :::....|     |
      /\     ,/ \      ;:::::;     ;
    .:. \:..|    :     ; '.--|     ;
   ::.  :''  `-.,,;     ;'   ;     ;
.-'. _.'\      / `;      \,__:      \
`---'    `----'   ;      /    \,.,,,/
                   `----`              ⠀⠀⠀⠀⠀⠀⠀⠀⠀
''')
