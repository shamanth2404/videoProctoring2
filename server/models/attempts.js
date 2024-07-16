const mongoose = require('mongoose');

const attemptSchema = new mongoose.Schema({     
    email:{
        type: String,
        unique: true,
        required: true,
    },
    tests:[{
        testCode:{
            type: String,
            required: true,
        },
        testScore:{
            type: Number,
            default: 0,
        },
        warnings: [{
            warningType:{
                type: String,                
            },
            warningCount:{
                type: Number,
                default: 0,
            },
        }],
        createdAt: {
            type: Date,
            default: Date.now,
        },
    }]
}, { timestamps: true });



module.exports = mongoose.model('Attempts', attemptSchema);