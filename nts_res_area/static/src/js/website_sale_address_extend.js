/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.websiteSaleAddress.include({
    events: Object.assign({}, publicWidget.registry.websiteSaleAddress.prototype.events, {
        "change select[name='state_id']": "_onChangeStateExtended",
        "blur input[name='phone'] ": "_onValidatePhone", // Add event for phone validation
        "blur input[name='mobile'] ": "_onValidatePhone", // Add event for phone validation
    }),

    /**
     * Extend the original _onChangeState handler to fetch areas.
     */
    _onChangeStateExtended(ev) {
        // Call the original _onChangeState if needed
        if (this._onChangeState) {
            this._onChangeState(ev);
        }

        const stateId = parseInt(this.addressForm.state_id.value);
        const areaSelect = this.addressForm.querySelector('[name="area_id"]');

        if (!stateId || !areaSelect) return;

        // Clear old options except the placeholder
        areaSelect.options.length = 1;

        return rpc('/shop/state_areas', { state_id: stateId }).then((areas) => {
            if (areas && areas.length) {
                areas.forEach(area => {
                    const option = new Option(area.name, area.id);
                    areaSelect.appendChild(option);
                });
                this._showInput('area_id');
            } else {
                this._hideInput('area_id');
            }
        });
    },

    /**
     * Validate the phone field.
     */
     _onValidatePhone(ev) {
        const phoneInput = ev.target;
        const phoneValue = phoneInput.value.trim();
        const phonePattern = /^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s./0-9]{9,}$/;
        const inputName = phoneInput.getAttribute('name');
        let errorSpan = null;
        console.log(inputName);
        if (inputName === 'phone' ) {
              errorSpan = document.getElementById("phone_error");
        }
        else if (inputName === 'mobile') {
             errorSpan = document.getElementById("mobile_error");
        }
        const isValid = phonePattern.test(phoneValue);
        console.log(errorSpan);
        if (errorSpan) {
            errorSpan.style.display = isValid ? "none" : "inline";
        }

        const submitButton = this.addressForm.querySelector('button[id="save_address"]');
        if (submitButton) {
            submitButton.disabled = !isValid;
        }
    },

});