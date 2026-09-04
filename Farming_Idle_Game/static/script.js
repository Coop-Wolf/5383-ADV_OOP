// ====================
// Update Game
// ====================

async function updateGame() {

    const response = await fetch("/game");
    const game = await response.json();


    // ====================
    // Basic Stats
    // ====================

    const moneyElement = document.getElementById("money");

    const incomeElement = document.getElementById("income");


    if (moneyElement) {
        moneyElement.textContent = formatMoney(game.money);
    }


    if (incomeElement) {
        incomeElement.textContent = formatMoney(game.income_per_second);
    }


    // ====================
    // Prestige Stats
    // ====================

    const prestigePointsElement =
        document.getElementById("prestige-points");

    const prestigeBonusElement =
        document.getElementById("prestige-bonus");

    const prestigeTotalBonusElement =
        document.getElementById("prestige-total-bonus");

    const prestigeRequirementElement =
        document.getElementById("prestige-requirement");


    if (prestigePointsElement) {
        prestigePointsElement.textContent =
            game.prestige_points;
    }


    const prestigeBonus =
        (game.prestige_multiplier - 1) * 100;


    if (prestigeBonusElement) {
        prestigeBonusElement.textContent =
            prestigeBonus.toFixed(0);
    }


    if (prestigeTotalBonusElement) {
        prestigeTotalBonusElement.textContent =
            prestigeBonus.toFixed(0);
    }


    if (prestigeRequirementElement) {
        prestigeRequirementElement.textContent =
            game.prestige_requirement.toLocaleString();
    }


    // ====================
    // Prestige Button
    // ====================

    const prestigeButton =
        document.getElementById("prestige-button");


    if (prestigeButton) {

        if (game.money >= game.prestige_requirement) {

            prestigeButton.disabled = false;
            prestigeButton.textContent = "Prestige";

        } else {

            prestigeButton.disabled = true;

            prestigeButton.textContent =
                "Need $" +
                game.prestige_requirement.toLocaleString();
        }
    }


    // ====================
    // Your Farm
    // ====================

    if (document.getElementById("farmers")) {

        renderEquipment(
            game.farmers,
            "farmers",
            "👨‍🌾",
            "farmer",
            "Farmer",
            game
        );


        renderEquipment(
            game.plows,
            "plows",
            "🚜",
            "plow",
            "Plow",
            game
        );


        renderEquipment(
            game.tractors,
            "tractors",
            "🚜",
            "tractor",
            "Tractor",
            game
        );


        renderEquipment(
            game.harvesters,
            "harvesters",
            "🌾",
            "harvester",
            "Harvester",
            game
        );


        renderEquipment(
            game.crop_dusters,
            "crop-dusters",
            "✈️",
            "crop-duster",
            "Crop Duster",
            game
        );


        renderEquipment(
            game.drones,
            "drones",
            "🚁",
            "drone",
            "Drone",
            game
        );
    }


    // ====================
    // Shop
    // ====================

    if (document.getElementById("farmer-shop")) {

        renderShop(
            game.farmer_types,
            "farmer-shop",
            "👨‍🌾",
            "farmer",
            "Farmer",
            game
        );


        renderShop(
            game.plow_types,
            "plow-shop",
            "🚜",
            "plow",
            "Plow",
            game
        );


        renderShop(
            game.tractor_types,
            "tractor-shop",
            "🚜",
            "tractor",
            "Tractor",
            game
        );


        renderShop(
            game.harvester_types,
            "harvester-shop",
            "🌾",
            "harvester",
            "Harvester",
            game
        );


        renderShop(
            game.crop_duster_types,
            "crop-duster-shop",
            "✈️",
            "crop-duster",
            "Crop Duster",
            game
        );


        renderShop(
            game.drone_types,
            "drone-shop",
            "🚁",
            "drone",
            "Drone",
            game
        );
    }

    // ====================
    // Achievements
    // ====================

    if (document.getElementById("achievements")) {

        renderAchievements(game.achievements);

    }
}


// ====================
// Render Owned Equipment
// ====================

function renderEquipment(
    equipment,
    containerId,
    icon,
    type,
    displayName,
    game
) {

    const container =
        document.getElementById(containerId);

    if (!container) {
        return;
    }

    container.innerHTML = "";


    if (equipment.length === 0) {

        container.innerHTML =
            `<p class="empty-message">
                No ${displayName.toLowerCase()}s owned.
            </p>`;

        return;
    }


    equipment.forEach((item, index) => {

        const card =
            document.createElement("div");

        card.className = "equipment-card";


        const maxLevel =
            item.level >= 10;

        const cannotAfford =
            game.money < item.upgrade_cost;

        const progress =
            (item.level / 10) * 100;


        let buttonText =
            `Upgrade — $${formatMoney(item.upgrade_cost)}`;

        let buttonDisabled =
            false;


        if (maxLevel) {

            buttonText = "Max Level";
            buttonDisabled = true;

        } else if (cannotAfford) {

            buttonDisabled = true;
        }


        card.innerHTML = `

            <h4>
                ${icon} ${item.name}
            </h4>

            <div class="equipment-info">

                <span class="level">
                    Level ${item.level}/10
                </span>

                <span class="profit">
                    $${formatMoney(item.profit)}/sec
                </span>

            </div>


            <div class="level-bar">

                <div
                    class="level-progress"
                    style="width: ${progress}%">
                </div>

            </div>


            <button
                onclick="upgradeEquipment('${type}', ${index})"
                ${buttonDisabled ? "disabled" : ""}
            >
                ${buttonText}
            </button>

        `;


        container.appendChild(card);
    });
}


// ====================
// Render Shop
// ====================

// ====================
// Render Shop
// ====================

function renderShop(
    equipmentTypes,
    containerId,
    icon,
    type,
    displayName,
    game
) {

    const container =
        document.getElementById(containerId);

    if (!container) {
        return;
    }

    container.innerHTML = "";


    // Get how many of this equipment type are owned
    const equipmentCount =
        getEquipmentCount(type, game);


    equipmentTypes.forEach((item, index) => {

        const card =
            document.createElement("div");

        card.className = "shop-card";


        const maxEquipment =
            equipmentCount >= 6;

        const cannotAfford =
            game.money < item.cost;


        let buttonText =
            "Buy";

        let buttonDisabled =
            false;


        if (maxEquipment) {

            buttonText =
                `Max ${displayName}s`;

            buttonDisabled = true;

        } else if (cannotAfford) {

            buttonText =
                `Need $${formatMoney(item.cost)}`;

            buttonDisabled = true;
        }


        card.innerHTML = `

            <h4>
                ${icon} ${item.name}
            </h4>

            <div class="shop-price">
                $${formatMoney(item.cost)}
            </div>

            <div class="shop-income">
                +$${formatMoney(item.profit)}/sec
            </div>

            <div class="shop-owned">
                ${equipmentCount} / 6 owned
            </div>

            <button
                onclick="buyEquipment('${type}', ${index})"
                ${buttonDisabled ? "disabled" : ""}
            >
                ${buttonText}
            </button>

        `;


        container.appendChild(card);
    });
}


function renderAchievements(achievements) {

    const container =
        document.getElementById("achievements");

    if (!container) {
        return;
    }

    container.innerHTML = "";


    let unlockedCount = 0;


    achievements.forEach(achievement => {

        if (achievement.unlocked) {
            unlockedCount++;
        }


        const card =
            document.createElement("div");

        card.className =
            achievement.unlocked
                ? "achievement-card unlocked"
                : "achievement-card locked";


        let progressText =
            `${achievement.progress} / ${achievement.requirement}`;


        // Format money achievements
        if (
            achievement.id === "big_money" ||
            achievement.id === "millionaire"
        ) {

            progressText =
                `$${achievement.requirement.toLocaleString()}`;

        }


        card.innerHTML = `

            <div class="achievement-icon">
                ${achievement.unlocked ? "🏆" : "🔒"}
            </div>

            <div class="achievement-content">

                <h3>
                    ${achievement.name}
                </h3>

                <p>
                    ${achievement.description}
                </p>

                <div class="achievement-progress">
                    ${progressText}
                </div>

                <div class="achievement-status">
                    ${
                        achievement.unlocked
                            ? "✓ Unlocked"
                            : "Locked"
                    }
                </div>

            </div>

        `;


        container.appendChild(card);

    });


    // Update achievement counter

    const countElement =
        document.getElementById("achievement-count");


    if (countElement) {

        countElement.textContent =
            `${unlockedCount} / ${achievements.length} unlocked`;

    }

}


// ====================
// Get Equipment Count
// ====================

function getEquipmentCount(type, game) {

    const equipment = {

        farmer: game.farmers,

        plow: game.plows,

        tractor: game.tractors,

        harvester: game.harvesters,

        "crop-duster": game.crop_dusters,

        drone: game.drones

    };


    return equipment[type].length;
}


// ====================
// Buy Equipment
// ====================

async function buyEquipment(type, index) {

    await fetch(
        `/buy/${type}/${index}`,
        {
            method: "POST"
        }
    );


    updateGame();
}


// ====================
// Upgrade Equipment
// ====================

async function upgradeEquipment(type, index) {

    await fetch(
        `/upgrade/${type}/${index}`,
        {
            method: "POST"
        }
    );


    updateGame();
}


function formatMoney(amount) {
    if (amount >= 1000000000) {
        return `${(amount / 1000000000).toFixed(1)}B`;
    }

    if (amount >= 1000000) {
        return `${(amount / 1000000).toFixed(1)}M`;
    }

    if (amount >= 1000) {
        return `${(amount / 1000).toFixed(1)}K`;
    }

    return `${amount.toFixed(2)}`;
}



// ====================
// Prestige
// ====================

async function prestige() {

    const response =
        await fetch(
            "/prestige",
            {
                method: "POST"
            }
        );


    const result =
        await response.json();


    if (result.success) {

        updateGame();

    }
}


// ====================
// Start Game
// ====================

updateGame();

setInterval(updateGame, 1000);