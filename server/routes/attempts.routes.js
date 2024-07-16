const express = require('express');
const router = express.Router();
const {attemptedTest, addAttempt, deleteAttempt, addWarning, getWarnings, attempts, getAllWarnings} = require('../controllers/attempt.control');


router.get('/attempted-test', attemptedTest); //To check if test is already attempted by the student
router.post('/add-attempt',addAttempt);
router.delete('/deleteattempt',deleteAttempt);
router.put('/add-warning',addWarning);
router.get('/get-warning',getWarnings);
router.get('/get-all-warnings',getAllWarnings);
router.get('/getAttempts',attempts);

module.exports = router;