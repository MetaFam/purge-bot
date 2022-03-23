class ROLE:
    PLAYER = "player"
    PATRON = "patron"
    BRONZE_FAM = "BRONZE FAM"
    SILVER_FAM = "SILVER FAM"
    GOLDEN_FAM = "GOLDEN FAM"
    PLATINUM_FAM = "PLATINUM FAM"
    DIAMOND_FOUNDER = "DIAMOND FOUNDER"
    OTHERS = "OTHERS"

    PLAYER_ROLES = [PLAYER, BRONZE_FAM, SILVER_FAM, GOLDEN_FAM, PLATINUM_FAM, DIAMOND_FOUNDER]

    def get_broad_role(role):
        if role == ROLE.PATRON:
            return ROLE.PATRON
        elif role in ROLE.PLAYER_ROLES:
            return ROLE.PLAYER
        else:
            return ROLE.OTHERS

BIG_DAYS_VALUE = 365